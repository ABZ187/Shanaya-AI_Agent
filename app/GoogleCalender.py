import datetime
import os.path
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
load_dotenv()
OAuth_JSON = os.environ["OAuth_JSON"]


def google_calender_authenticate(OAuth_JSON):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(OAuth_JSON, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")


service = google_calender_authenticate(OAuth_JSON)


def create_calender_event(
    event_name: str, event_desc: str, start_datetime: str, end_datetime: str
) -> None:
    """
    Create a Google Calender event to remind the user of task or a event.
    Args:
        event_name: str - Name of the event or task.
        event_desc: str - Description of the event or task
        start_datetime: str - Start date and time of event or task in format YYYY-MM-DDTHH:MM:SS
        end_datetime: str - End date and time of event or task in format YYYY-MM-DDTHH:MM:SS

    E.g: Coffee with Sam for next AI project discussion on 21st March 2024 at 5:30 in evening.
    event_name = Coffee with Sam
    event_desc = Disccusing upcoming AI projects at the company.
    start_datetime = 2024-03-21T17:30:00
    end_datetime = 2024-03-21T18:30:00

    """
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    event = {
        "summary": event_name,
        # "location": "800 Howard St., San Francisco, CA 94103",
        "description": event_desc,
        "start": {
            # "dateTime": "2024-12-06T20:00:00+05:30",
            "dateTime": start_datetime + "+05:30",
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            # "dateTime": "2024-12-06T21:00:00+05:30",
            "dateTime": end_datetime + "+05:30",
            "timeZone": "Asia/Kolkata",
        },
        # "recurrence": ["RRULE:FREQ=DAILY;COUNT=2"],
        # "attendees": [
        # {"email": "lpage@example.com"},
        # {"email": "sbrin@example.com"},
        # ],
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 24 * 60},
                {"method": "popup", "minutes": 10},
            ],
        },
    }
    try:
        event = service.events().insert(calendarId="primary", body=event).execute()
        print("Event created: %s" % (event.get("htmlLink")))
    except HttpError as error:
        print(f"An error occurred while creating event: {error}")


def main():
    create_calender_event(
        event_name="event1",
        event_desc="desc",
        start_datetime="2024-12-06T20:00:00+05:30",
        end_datetime="2024-12-06T20:00:00+05:30",
    )
