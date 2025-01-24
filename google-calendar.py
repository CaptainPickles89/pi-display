from __future__ import print_function
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto

# Scopes for read-only access to your calendar
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_authenticated_service():
    creds = None
    if os.path.exists("./creds/token.json"):
        creds = Credentials.from_authorized_user_file("./creds/token.json", SCOPES)

    # If no valid credentials, force the authentication flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())  # Refresh the token
            except Exception as e:
                print(f"Error refreshing token: {e}")
                creds = None
        if not creds:
            # Start the full authorization flow if no refresh token or creds invalid
            flow = InstalledAppFlow.from_client_secrets_file("./creds/client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("./creds/token.json", "w") as token_file:
            token_file.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

def get_calendar_events():
    # Load credentials & build the service
    service = get_authenticated_service()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # Get all calendar IDs
    all_calendars = service.calendarList().list().execute()

    events = []
    for calendar in all_calendars["items"]:
        calendar_id = calendar["id"]

        # Skip the "birthdays" calendar from Google Contacts
        if 'birthday@group.v.calendar.google.com' in calendar_id:
            print(f"Skipping birthdays calendar: {calendar_id}")
            continue

        # Skip specific calendars (e.g., Holidays)
        if calendar_id.endswith('#holiday@group.v.calendar.google.com'):
            print(f"Skipping calendar: {calendar_id}")
            continue

        try:
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
        except Exception as e:
            print(f"Error fetching events for calendar {calendar_id}: {e}")
            continue

        # Filter events
        for event in events_result.get("items", []):
            if "birthday" in event["summary"].lower():
                print(f"Skipping contacts birthdays")
                continue
            event["calendarId"] = calendar_id
            events.append(event)

    return events

# Fetch and print calendar events
events = get_calendar_events()
print(f"----------------------")
print(f"Getting events now")
print(f"----------------------")
for event in events:
    start = event["start"].get("dateTime", event["start"].get("date"))
    calendar_id = event.get("calendarId", "Unknown")
    print(f"{start} - {event['summary']} (Calendar ID: {calendar_id})")

def display_events():
    events = get_calendar_events()

    try:
        # Prepare the display
        inky = auto()
        img = Image.open("./resources/imgs/pihole-bg1-01.png")
        draw = ImageDraw.Draw(img)

        # Font settings (update path to your font file)
        font_path = "./resources/fonts/Roboto-Medium.ttf"
        font = ImageFont.truetype(font_path, 45)

        # Measure text size
        text_bbox = draw.multiline_textbbox((0, 0), events, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Calculate position to center the text
        image_width, image_height = img.size
        x_position = (image_width - text_width) // 2
        y_position = (image_height - text_height) // 2

        # Draw the text on the image
        draw.multiline_text((x_position, y_position), events, font=font, align='center', fill=0)  # Black text
        # Show on the Inky
        inky.set_image(img)
        inky.show()
        return 0
    except Exception as e:
        print(f"Error Displaying Events: {e}")
        return None

if __name__ == "__main__":
    display_events()