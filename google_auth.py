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

# Handle both development and production domains
REPLIT_DOMAIN = os.environ.get("REPL_SLUG") + "." + os.environ.get("REPL_OWNER") + ".repl.co" if "REPL_SLUG" in os.environ else None
REPLIT_DEV_DOMAIN = os.environ.get("REPLIT_DEV_DOMAIN")

client = WebApplicationClient(GOOGLE_CLIENT_ID) if GOOGLE_CLIENT_ID else None
google_auth = Blueprint("google_auth", __name__)

@google_auth.route("/google_login")
def login():
    if not GOOGLE_CLIENT_ID:
        flash("Google OAuth is not configured. Please set up your credentials.", "warning")
        return redirect(url_for("index"))

    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use the appropriate domain for the callback
    callback_domain = f"https://{REPLIT_DOMAIN}" if REPLIT_DOMAIN else request.base_url.replace("http://", "https://")
    callback_uri = f"{callback_domain}/google_login/callback"
    
    logger.debug(f"OAuth callback URI: {callback_uri}")

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=callback_uri,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@google_auth.route("/google_login/callback")
def callback():
    if not GOOGLE_CLIENT_ID:
        return redirect(url_for("index"))

    code = request.args.get("code")
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Use the appropriate domain for the callback
    callback_domain = f"https://{REPLIT_DOMAIN}" if REPLIT_DOMAIN else request.base_url.replace("http://", "https://")
    callback_uri = callback_domain.rstrip('/') + '/google_login/callback'
    
    logger.debug(f"OAuth callback verification URI: {callback_uri}")

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

    login_user(user)
    return redirect(url_for("index"))

@google_auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))