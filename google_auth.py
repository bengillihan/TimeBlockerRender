import json
import os
import time
import requests
import logging
from typing import Tuple
from app import db
from flask import Blueprint, redirect, request, url_for, flash, current_app
from flask_login import login_required, login_user, logout_user
from models import User
from oauthlib.oauth2 import WebApplicationClient

logger = logging.getLogger(__name__)

# Google OAuth config
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
GOOGLE_REQUEST_TIMEOUT = 10  # seconds; keeps a slow Google response from tying up a worker
DISCOVERY_CACHE_TTL = 3600  # Google's endpoints rarely change

_discovery_cache = {"config": None, "fetched_at": 0.0}

logger.info("Initializing Google OAuth configuration")

google_auth = Blueprint("google_auth", __name__)

def get_oauth_client() -> WebApplicationClient:
    """Create a fresh client per request; the client stores tokens, so it must not be shared between users."""
    return WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg() -> dict:
    """Return Google's OpenID configuration, cached for an hour."""
    now = time.monotonic()
    if _discovery_cache["config"] is None or now - _discovery_cache["fetched_at"] > DISCOVERY_CACHE_TTL:
        response = requests.get(GOOGLE_DISCOVERY_URL, timeout=GOOGLE_REQUEST_TIMEOUT)
        response.raise_for_status()
        _discovery_cache["config"] = response.json()
        _discovery_cache["fetched_at"] = now
    return _discovery_cache["config"]

def get_callback_url():
    """Get the appropriate callback URL based on the current request."""
    # Always use HTTPS for OAuth callbacks
    base_url = f"https://{request.host}"
    callback_url = f"{base_url}/google_login/callback"
    logger.info(f"Generated callback URL: {callback_url}")
    return callback_url

@google_auth.route("/google_login")
def login():
    if not GOOGLE_CLIENT_ID:
        logger.error("Google OAuth credentials not configured")
        flash("Google OAuth is not configured. Please set up your credentials.", "warning")
        return redirect(url_for("index"))

    try:
        google_provider_cfg = get_google_provider_cfg()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        # Get the callback URL for the current environment
        callback_url = get_callback_url()
        logger.info(f"Starting OAuth flow with callback URL: {callback_url}")

        # Prepare OAuth request with basic scopes only (no calendar access)
        request_uri = get_oauth_client().prepare_request_uri(
            authorization_endpoint,
            redirect_uri=callback_url,
            scope=[
                "openid",
                "email",
                "profile"
            ],
        )

        logger.debug(f"Generated OAuth request URI: {request_uri}")
        return redirect(request_uri)
    except Exception as e:
        logger.error(f"Error during OAuth login: {str(e)}")
        flash("Error connecting to Google. Please try again.", "error")
        return redirect(url_for("index"))

@google_auth.route("/google_login/callback")
def callback():
    if not GOOGLE_CLIENT_ID:
        return redirect(url_for("index"))

    try:
        code = request.args.get("code")
        if not code:
            logger.error("No OAuth code received in callback")
            flash("Authentication failed - no code received.", "error")
            return redirect(url_for("index"))

        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]

        callback_url = get_callback_url()
        logger.info(f"Processing OAuth callback with URL: {callback_url}")

        # Always use HTTPS for the authorization response
        current_url = request.url.replace('http://', 'https://')

        # Exchange code for token
        client = get_oauth_client()
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=current_url,
            redirect_url=callback_url,
            code=code,
        )

        if not token_url.startswith("https://"):
            logger.error("Token URL must use HTTPS")
            flash("Authentication configuration error.", "error")
            return redirect(url_for("index"))

        # Ensure auth tuple has proper typing
        auth: Tuple[str, str] = (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=auth,
            timeout=GOOGLE_REQUEST_TIMEOUT,
        )

        # Check token response
        if not token_response.ok:
            logger.error(f"Token exchange failed: {token_response.text}")
            flash("Failed to complete authentication. Please try again.", "error")
            return redirect(url_for("index"))

        client.parse_request_body_response(json.dumps(token_response.json()))

        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body, timeout=GOOGLE_REQUEST_TIMEOUT)

        userinfo = userinfo_response.json()
        if userinfo.get("email_verified"):
            users_email = userinfo["email"]
            users_name = userinfo["given_name"]
        else:
            return "User email not available or not verified by Google.", 400

        user = User.query.filter_by(email=users_email).first()
        if not user:
            user = User(username=users_name, email=users_email)
            db.session.add(user)
            db.session.commit()

        # Generate new session ID and invalidate other sessions
        new_session_id = user.generate_new_session()
        
        login_user(user)
        
        # Store session ID in Flask session for validation
        from flask import session
        session['user_session_id'] = new_session_id

        flash("Successfully logged in!", "success")
        return redirect(url_for("index"))
    except Exception as e:
        logger.error(f"Error during OAuth callback: {str(e)}")
        flash("Error during Google authentication. Please try again.", "error")
        return redirect(url_for("index"))

@google_auth.route("/logout")
@login_required
def logout():
    # Invalidate user's session
    from flask_login import current_user
    from flask import session
    if current_user.is_authenticated:
        current_user.invalidate_session()
    
    # Clear Flask session
    session.pop('user_session_id', None)
    
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for("login"))