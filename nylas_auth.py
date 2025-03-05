import os
from urllib.parse import urlencode
from flask import Blueprint, redirect, request, url_for, flash, current_app
from flask_login import current_user, login_required
import requests
import logging

logger = logging.getLogger(__name__)

nylas_auth = Blueprint('nylas_auth', __name__)

def verify_nylas_config():
    """Verify required Nylas configuration is present."""
    required_vars = ['NYLAS_CLIENT_ID', 'NYLAS_CLIENT_SECRET', 'REPLIT_DOMAIN']
    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

def get_nylas_oauth_url():
    """Generate Nylas OAuth URL."""
    verify_nylas_config()

    # Ensure we use HTTPS for production
    replit_domain = os.environ.get('REPLIT_DOMAIN')
    redirect_uri = f"https://{replit_domain}/nylas/callback"

    logger.info(f"Configured Nylas redirect URI: {redirect_uri}")

    params = {
        'client_id': os.environ.get('NYLAS_CLIENT_ID'),
        'response_type': 'code',
        'scope': 'calendar.read_only',
        'redirect_uri': redirect_uri,
        'login_hint': current_user.email if current_user.email else None,
        'state': 'nylas_oauth'  # Add state parameter for security
    }

    auth_url = f"https://login.nylas.com/oauth/authorize?{urlencode(params)}"
    logger.info(f"Generated Nylas auth URL for user {current_user.email}")
    return auth_url

@nylas_auth.route('/nylas/auth')
@login_required
def auth():
    """Redirect user to Nylas OAuth."""
    try:
        verify_nylas_config()
        auth_url = get_nylas_oauth_url()
        logger.info(f"Redirecting user {current_user.email} to Nylas auth")
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"Error initiating Nylas auth: {str(e)}")
        flash("Failed to start authentication process. Please try again.", "error")
        return redirect(url_for('calendar_settings'))

@nylas_auth.route('/nylas/callback')
@login_required
def callback():
    """Handle OAuth callback from Nylas."""
    try:
        verify_nylas_config()

        code = request.args.get('code')
        error = request.args.get('error')
        error_description = request.args.get('error_description')
        state = request.args.get('state')

        if error or not code:
            logger.error(f"OAuth error for user {current_user.email}: {error} - {error_description}")
            flash(f'Authorization failed: {error_description or "Please try again."}', 'error')
            return redirect(url_for('calendar_settings'))

        if state != 'nylas_oauth':
            logger.error(f"Invalid state parameter received for user {current_user.email}")
            flash('Invalid authentication state. Please try again.', 'error')
            return redirect(url_for('calendar_settings'))

        logger.info(f"Exchanging code for access token for user {current_user.email}")
        response = requests.post('https://api.nylas.com/oauth/token', data={
            'client_id': os.environ.get('NYLAS_CLIENT_ID'),
            'client_secret': os.environ.get('NYLAS_CLIENT_SECRET'),
            'grant_type': 'authorization_code',
            'code': code
        })

        if response.status_code != 200:
            logger.error(f"Token exchange failed for user {current_user.email}: {response.text}")
            flash('Failed to complete authentication. Please try again.', 'error')
            return redirect(url_for('calendar_settings'))

        token_data = response.json()
        logger.info(f"Successfully obtained access token for user {current_user.email}")

        # Update the user's model with the token
        from app import db
        current_user.nylas_access_token = token_data['access_token']
        db.session.commit()
        logger.info(f"Saved access token for user {current_user.id}")

        flash('Successfully connected to Nylas!', 'success')
        return redirect(url_for('calendar_settings'))

    except Exception as e:
        logger.error(f"Error in Nylas callback for user {current_user.email}: {str(e)}")
        flash('An error occurred during authentication. Please try again.', 'error')
        return redirect(url_for('calendar_settings'))