from datetime import datetime, timedelta
import os
from nylas import APIClient
import logging
import pytz

logger = logging.getLogger(__name__)

def get_calendar_events(access_token, selected_date):
    """Fetch calendar events for the selected date using Nylas API."""
    try:
        if not access_token:
            logger.error("No Nylas access token available")
            return []

        nylas = APIClient(
            os.environ.get('NYLAS_CLIENT_ID'),
            os.environ.get('NYLAS_CLIENT_SECRET'),
            access_token,
            api_server="https://api.nylas.com"  # Updated API endpoint
        )

        # Convert date to timestamp range
        pacific = pytz.timezone('America/Los_Angeles')
        start_of_day = datetime.combine(selected_date, datetime.min.time())
        start_of_day = pacific.localize(start_of_day)
        end_of_day = start_of_day + timedelta(days=1)

        logger.info(f"Fetching Nylas calendar events for date: {selected_date}")

        # Fetch events for the day
        events = nylas.events.where(
            starts_after=start_of_day.timestamp(),
            ends_before=end_of_day.timestamp()
        )

        formatted_events = []
        for event in events:
            # Convert timestamps to datetime objects
            start_time = datetime.fromtimestamp(event.when['start_time'], tz=pacific)
            end_time = datetime.fromtimestamp(event.when['end_time'], tz=pacific)

            formatted_events.append({
                'summary': event.title,
                'start_time': start_time.strftime('%H:%M'),
                'end_time': end_time.strftime('%H:%M'),
                'description': event.description or '',
                'calendar_name': event.calendar_id,
                'color': event.get('colorId', '1')  # Added color support
            })

        logger.info(f"Retrieved {len(formatted_events)} events from Nylas")
        return sorted(formatted_events, key=lambda x: x['start_time'])

    except Exception as e:
        logger.error(f"Error fetching Nylas calendar events: {str(e)}")
        return []