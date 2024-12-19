import datetime
from GoogleCalender import service

from googleapiclient.errors import HttpError


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
    # now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
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


def multiply(a: int, b: int) -> int:
    """Multiply a and b
    Args:
        a: first int
        b: second int"""
    return a * b


def add(a: int, b: int) -> int:
    """Add a and b
    Args:
        a: first int
        b: second int"""
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtract a and b
    Args:
        a: first int
        b: second int"""
    return a - b
