from __future__ import print_function
import datetime as dt
import os.path
import threading
import os
import sys
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
            flow = InstalledAppFlow.from_client_secrets_file("./creds/client_secret.json", SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob")
            # Get the authorization URL
            auth_url, _ = flow.authorization_url(prompt='consent')

            print("Please go to this URL and authorize the application: ", auth_url)

            # Input with timeout mechanism
            auth_code = None
            timeout = 60  # Set your desired timeout in seconds

            def get_user_input():
                nonlocal auth_code
                try:
                    auth_code = input("Enter the authorization code: ")
                except Exception as e:
                    print(f"Error during input: {e}")
            
            input_thread = threading.Thread(target=get_user_input)
            input_thread.start()
            input_thread.join(timeout=timeout)

            if auth_code is None:
                print("\nAuthentication timed out. Please try again.")
                return None

            # Fetch the token using the authorization code
            flow.fetch_token(authorization_response=f'{auth_url}&code={auth_code}')

            # Now you can use the credentials
            creds = flow.credentials

        # Save the credentials for the next run
        with open("./creds/token.json", "w") as token_file:
            token_file.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

def get_calendar_events():
    # Load credentials & build the service
    service = get_authenticated_service()
    now = dt.datetime.now(dt.timezone.utc).isoformat()

    if not service:
        print(f"Failed to authenticate with Google")
        display_failure()

    
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
                maxResults=5,
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

def display_events():
    message = []
    events = get_calendar_events()
    for event in events:
        raw_start = event["start"].get("dateTime", event["start"].get("date"))
        try:
            # Parse the raw_start string into a datetime object
            parsed_start = dt.datetime.strptime(raw_start, "%Y-%m-%dT%H:%M:%SZ")  # For dateTime format
            formatted_start = parsed_start.strftime("%d-%b %H:%M")
        except ValueError:
            # Handle cases where the start date doesn't include time (e.g., "2025-01-24")
            parsed_start = dt.datetime.strptime(raw_start, "%Y-%m-%d")  # For date format
            formatted_start = parsed_start.strftime("%d-%b")
    
        event_summary = f"{formatted_start} \n {event['summary']}"
        print(f"{formatted_start} - {event['summary']}")
        message.append(event_summary)        

    try:
        # Prepare the display
        inky = auto()
        img = Image.open("./resources/imgs/birthday-bg1-01.png")
        draw = ImageDraw.Draw(img)

        # Set the message
        final_message = "\n".join(message)

        # Font settings (update path to your font file)
        font_path = "./resources/fonts/Roboto-Medium.ttf"
        font = ImageFont.truetype(font_path, 25)

        # Measure text size
        text_bbox = draw.multiline_textbbox((0, 0), final_message, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Calculate position to center the text
        image_width, image_height = img.size
        x_position = (image_width - text_width) // 2
        y_position = (image_height - text_height) // 2

        # Draw the text on the image
        draw.multiline_text((x_position, y_position), final_message, font=font, align='center', fill=0)  # Black text
        # Show on the Inky
        inky.set_image(img)
        inky.show()
        return 0
    except Exception as e:
        print(f"Error Displaying Events: {e}")
        return None
    
def display_failure():
    # Prepare the display
    inky = auto()
    img = Image.open("./resources/imgs/birthday-bg1-01.png")
    
    # Show on the Inky
    inky.set_image(img)
    inky.show()
    return 0

if __name__ == "__main__":
    display_events()