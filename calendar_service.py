from datetime import datetime, timedelta
import os
import google.oauth2.credentials
from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)

def get_calendar_list(credentials_info):
    """Fetch list of user's calendars."""
    try:
        logger.debug(f"Creating credentials with token info")
        credentials = google.oauth2.credentials.Credentials(
            token=credentials_info.get('token'),
            refresh_token=credentials_info.get('refresh_token'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
            client_secret=os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET"),
        )

        logger.debug("Building Calendar API service")
        service = build('calendar', 'v3', credentials=credentials)

        logger.debug("Fetching calendar list")
        calendar_list = service.calendarList().list().execute()

        logger.info(f"Successfully fetched calendar list")
        logger.debug(f"Found {len(calendar_list.get('items', []))} calendars")

        calendars = [{
            'id': calendar['id'],
            'summary': calendar['summary'],
            'primary': calendar.get('primary', False),
            'selected': calendar.get('selected', True)
        } for calendar in calendar_list.get('items', [])]

        logger.debug(f"Calendar details: {calendars}")
        return calendars
    except Exception as e:
        logger.error(f"Error fetching calendar list: {str(e)}")
        return []

def get_calendar_events(credentials_info, selected_date, calendar_ids=None):
    """Fetch calendar events for the selected date."""
    try:
        logger.debug(f"Creating credentials with token info")
        credentials = google.oauth2.credentials.Credentials(
            token=credentials_info.get('token'),
            refresh_token=credentials_info.get('refresh_token'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
            client_secret=os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET"),
        )

        logger.debug("Building Calendar API service")
        service = build('calendar', 'v3', credentials=credentials)
        logger.debug(f"Successfully created Calendar API service")

        start_of_day = datetime.combine(selected_date, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)

        formatted_events = []
        calendars_to_check = calendar_ids if calendar_ids else ['primary']
        logger.debug(f"Checking calendars: {calendars_to_check}")

        for calendar_id in calendars_to_check:
            try:
                logger.debug(f"Fetching events for calendar: {calendar_id}")
                events_result = service.events().list(
                    calendarId=calendar_id,
                    timeMin=start_of_day.isoformat() + 'Z',
                    timeMax=end_of_day.isoformat() + 'Z',
                    maxResults=50,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()

                events = events_result.get('items', [])
                logger.debug(f"Found {len(events)} events in calendar {calendar_id}")

                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    end = event['end'].get('dateTime', event['end'].get('date'))

                    try:
                        start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        end_time = datetime.fromisoformat(end.replace('Z', '+00:00'))

                        formatted_events.append({
                            'summary': event['summary'],
                            'start_time': start_time.strftime('%H:%M'),
                            'end_time': end_time.strftime('%H:%M'),
                            'description': event.get('description', ''),
                            'color': event.get('colorId', '1'),
                            'calendar_name': event.get('organizer', {}).get('displayName', 'Calendar')
                        })
                        logger.debug(f"Successfully formatted event: {event['summary']}")
                    except ValueError as e:
                        logger.error(f"Error parsing event times for {event.get('summary')}: {str(e)}")
                        continue

            except Exception as e:
                logger.error(f"Error fetching events for calendar {calendar_id}: {str(e)}")
                continue

        logger.debug(f"Total events found across all calendars: {len(formatted_events)}")
        return sorted(formatted_events, key=lambda x: x['start_time'])

    except Exception as e:
        logger.error(f"Error fetching calendar events: {str(e)}")
        return []