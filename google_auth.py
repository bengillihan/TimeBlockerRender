import json
import os
import requests
import logging
from app import db
from flask import Blueprint, redirect, request, url_for, flash
from flask_login import login_required, login_user, logout_user
from models import User
from oauthlib.oauth2 import WebApplicationClient

logger = logging.getLogger(__name__)

# Make credentials optional during development
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Get the Replit domain for OAuth callback
REPLIT_URL = "https://TimeBlocker-bdgillihan.replit.app"

logger.info(f"Configured Replit URL: {REPLIT_URL}")

print(f"""
To make Google authentication work:
1. Go to https://console.cloud.google.com/apis/credentials
2. Create a new OAuth 2.0 Client ID or edit existing one
3. Add this exact URL to Authorized redirect URIs:
   {REPLIT_URL}/google_login/callback

For detailed instructions, see:
https://docs.replit.com/tutorials/python/authentication-with-flask
""")

client = WebApplicationClient(GOOGLE_CLIENT_ID) if GOOGLE_CLIENT_ID else None
google_auth = Blueprint("google_auth", __name__)

@google_auth.route("/google_login")
def login():
    if not GOOGLE_CLIENT_ID:
        flash("Google OAuth is not configured. Please set up your credentials.", "warning")
        return redirect(url_for("index"))

    try:
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        # Log OAuth request details
        logger.info("Initiating Google OAuth login")
        logger.info(f"Redirect URI: {REPLIT_URL}/google_login/callback")

        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=f"{REPLIT_URL}/google_login/callback",
            scope=[
                "openid",
                "email",
                "profile",
                "https://www.googleapis.com/auth/calendar.readonly"
            ],
        )
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
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]

        callback_uri = f"{REPLIT_URL}/google_login/callback"
        logger.info(f"Processing OAuth callback at: {callback_uri}")

        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url.replace("http://", "https://"),
            redirect_url=callback_uri,
            code=code,
        )
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )

        # Parse the tokens
        client.parse_request_body_response(json.dumps(token_response.json()))

        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)

        userinfo = userinfo_response.json()
        if userinfo.get("email_verified"):
            users_email = userinfo["email"]
            users_name = userinfo["given_name"]
        else:
            logger.error("User email not verified by Google")
            return "User email not available or not verified by Google.", 400

        # Find or create user
        user = User.query.filter_by(email=users_email).first()
        if not user:
            user = User(username=users_name, email=users_email)
            db.session.add(user)

        # Store the credentials info for Calendar API access
        user.credentials_info = {
            'token': token_response.json().get('access_token'),
            'refresh_token': token_response.json().get('refresh_token'),
        }

        db.session.commit()
        login_user(user)

        flash("Successfully connected to Google Calendar!", "success")
        return redirect(url_for("index"))
    except Exception as e:
        logger.error(f"Error during OAuth callback: {str(e)}")
        flash("Error during Google authentication. Please try again.", "error")
        return redirect(url_for("index"))

@google_auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))