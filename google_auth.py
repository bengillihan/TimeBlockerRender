import json
import os
import requests
import logging
from typing import Optional, Tuple
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

logger.info("Initializing Google OAuth configuration")

client: Optional[WebApplicationClient] = WebApplicationClient(GOOGLE_CLIENT_ID) if GOOGLE_CLIENT_ID else None
google_auth = Blueprint("google_auth", __name__)

def get_callback_url():
    """Get the appropriate callback URL based on the current request."""
    # Always use HTTPS for OAuth callbacks
    base_url = f"https://{request.host}"
    callback_url = f"{base_url}/google_login/callback"
    logger.info(f"Generated callback URL: {callback_url}")
    return callback_url

@google_auth.route("/google_login")
def login():
    if not GOOGLE_CLIENT_ID or not client:
        logger.error("Google OAuth credentials not configured")
        flash("Google OAuth is not configured. Please set up your credentials.", "warning")
        return redirect(url_for("index"))

    try:
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        # Get the callback URL for the current environment
        callback_url = get_callback_url()
        logger.info(f"Starting OAuth flow with callback URL: {callback_url}")

        # Prepare OAuth request with basic scopes only (no calendar access)
        request_uri = client.prepare_request_uri(
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
    if not GOOGLE_CLIENT_ID or not client:
        return redirect(url_for("index"))

    try:
        code = request.args.get("code")
        if not code:
            logger.error("No OAuth code received in callback")
            flash("Authentication failed - no code received.", "error")
            return redirect(url_for("index"))

        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]

        callback_url = get_callback_url()
        logger.info(f"Processing OAuth callback with URL: {callback_url}")

        # Always use HTTPS for the authorization response
        current_url = request.url.replace('http://', 'https://')

        # Exchange code for token
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=current_url,
            redirect_url=callback_url,
            code=code,
        )

        # Ensure auth tuple has proper typing
        auth: Tuple[str, str] = (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=auth,
        )

        # Check token response
        if not token_response.ok:
            logger.error(f"Token exchange failed: {token_response.text}")
            flash("Failed to complete authentication. Please try again.", "error")
            return redirect(url_for("index"))

        client.parse_request_body_response(json.dumps(token_response.json()))

        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)

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
            
            # Import the function after the models are loaded
            from app import create_default_categories
            create_default_categories(user)

        login_user(user)

        flash("Successfully logged in!", "success")
        return redirect(url_for("index"))
    except Exception as e:
        logger.error(f"Error during OAuth callback: {str(e)}")
        flash("Error during Google authentication. Please try again.", "error")
        return redirect(url_for("index"))

@google_auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for("login"))