import os
from urllib.parse import urlencode
from flask import Blueprint, redirect, request, url_for, flash
from flask_login import current_user, login_required
import requests
import logging

logger = logging.getLogger(__name__)

nylas_auth = Blueprint('nylas_auth', __name__)

def get_nylas_oauth_url():
    """Generate Nylas OAuth URL."""
    params = {
        'client_id': os.environ.get('NYLAS_CLIENT_ID'),
        'response_type': 'code',
        'scope': 'calendar.read_only',
        'redirect_uri': url_for('nylas_auth.callback', _external=True)
    }
    return f"https://login.nylas.com/oauth/authorize?{urlencode(params)}"

@nylas_auth.route('/nylas/auth')
@login_required
def auth():
    """Redirect user to Nylas OAuth."""
    return redirect(get_nylas_oauth_url())

@nylas_auth.route('/nylas/callback')
@login_required
def callback():
    """Handle OAuth callback from Nylas."""
    code = request.args.get('code')
    if not code:
        flash('Authorization failed. Please try again.', 'error')
        return redirect(url_for('index'))

    try:
        # Exchange code for access token
        response = requests.post('https://api.nylas.com/oauth/token', data={
            'client_id': os.environ.get('NYLAS_CLIENT_ID'),
            'client_secret': os.environ.get('NYLAS_CLIENT_SECRET'),
            'grant_type': 'authorization_code',
            'code': code
        })

        if response.status_code != 200:
            logger.error(f"Error exchanging code for token: {response.text}")
            flash('Failed to authenticate with Nylas. Please try again.', 'error')
            return redirect(url_for('index'))

        token_data = response.json()

        # Update the user's model with the token
        from app import db
        current_user.nylas_access_token = token_data['access_token']
        db.session.commit()

        flash('Successfully connected to Nylas!', 'success')
        return redirect(url_for('index'))

    except Exception as e:
        logger.error(f"Error in Nylas callback: {str(e)}")
        flash('An error occurred during authentication. Please try again.', 'error')
        return redirect(url_for('index'))