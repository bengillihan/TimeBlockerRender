from datetime import datetime, timedelta
import os
import google.oauth2.credentials
from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)

def get_calendar_events(credentials_info, selected_date):
    """Fetch calendar events for the selected date."""
    try:
        # Create credentials object from the token info
        credentials = google.oauth2.credentials.Credentials(
            token=credentials_info.get('token'),
            refresh_token=credentials_info.get('refresh_token'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
            client_secret=os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET"),
        )

        # Build the calendar service
        service = build('calendar', 'v3', credentials=credentials)

        # Get the start and end of the selected date
        start_of_day = datetime.combine(selected_date, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)

        # Call the Calendar API
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_of_day.isoformat() + 'Z',
            timeMax=end_of_day.isoformat() + 'Z',
            maxResults=50,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        
        # Format events for display
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Convert to datetime objects
            start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end.replace('Z', '+00:00'))
            
            formatted_events.append({
                'summary': event['summary'],
                'start_time': start_time.strftime('%H:%M'),
                'end_time': end_time.strftime('%H:%M'),
                'description': event.get('description', ''),
                'color': event.get('colorId', '1')  # Default to blue if no color specified
            })
        
        return formatted_events

    except Exception as e:
        logger.error(f"Error fetching calendar events: {str(e)}")
        return []
