import requests
import traceback
import os
import json
from datetime import datetime, time
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont
from display import get_display

# station codes
bigs = "BIW"
st_p = "STP"
king = "KGX"

# Layout constants - tweak these as you go
FONT_PATH = "./resources/fonts/Roboto-Medium.ttf"
LOGO_PATH = "./resources/imgs/rail.png"

HEADER_HEIGHT = 90  # TODO: tune - height in px of the From / logo / To band
CARD_MARGIN_X = 20  # TODO: tune - left/right margin for the card rectangles
CARD_GAP = 10  # TODO: tune - vertical gap between cards
CARD_RADIUS = 15  # TODO: tune - corner radius for rounded_rectangle


def load_api_key():
    # Path to your creds directory where the API key is stored
    api_key_path = "./creds/rtt_token.txt"

    try:
        with open(api_key_path, "r") as f:
            long_api_key = f.read().strip()  # Remove any surrounding whitespace

            headers = {
                "Authorization": f"Bearer {long_api_key}",
                "Version": "2026-07-25",
                "Accept": "application/json",
            }

            response = requests.get(
                "https://data.rtt.io/api/get_access_token", headers=headers
            )
            response.raise_for_status()
            data = response.json()

            short_api_key = data["token"]

            if not short_api_key:
                print("Short life API key Empty")
                return None

            return short_api_key

    except FileNotFoundError:
        print(f"Error: API key file not found at {api_key_path}")
        return None

    except Exception as e:
        print(f"Error: {e}")


def in_between(now, start, end):
    if start <= end:
        return start <= now < end
    else:  # over midnight e.g., 23:30-04:15
        return start <= now or now < end


def get_timetable():

    api_key = load_api_key()
    url_base = "https://data.rtt.io/gb-nr/location?code="
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Version": "2026-07-25",
        "Accept": "application/json",
    }
    trains = []

    try:
        if in_between(datetime.now().time(), time(0), time(12)):
            print("Checking agaist morning trains")
            departing = "Biggleswade"
            calling = "St Pancras"
            response = requests.get(
                f"{url_base}{bigs}&filterTo={st_p}", headers=headers
            )
            response.raise_for_status()
            data = response.json()

        elif in_between(datetime.now().time(), time(12), time(20)):
            print("Checking agaist afternoon trains")
            departing = "Kings Cross"
            calling = "Biggleswade"
            response = requests.get(
                f"{url_base}{king}&filterTo={bigs}", headers=headers
            )
            response.raise_for_status()
            data = response.json()

        else:
            print("Checking agaist evening trains")
            departing = "St Pancras"
            calling = "Biggleswade"
            response = requests.get(
                f"{url_base}{st_p}&filterTo={bigs}", headers=headers
            )
            response.raise_for_status()
            data = response.json()

        for service in data["services"][:3]:
            departure_time = service["temporalData"]["departure"]["scheduleAdvertised"]
            estimated_time = service["temporalData"]["departure"]["realtimeForecast"]
            depature_station = departing
            calling_station = calling
            cancelled = service["temporalData"]["departure"]["isCancelled"]
            heading_to = service["destination"][0]["location"]["description"]
            platform = service["locationMetadata"]["platform"]["forecast"]
            coaches = service["locationMetadata"]["numberOfVehicles"]

            if estimated_time != departure_time and cancelled != True:
                delayed = True
            else:
                delayed = False

            trains.append(
                {
                    "heading_to": heading_to,
                    "departing_from": depature_station,
                    "calling_at": calling_station,
                    "departure": departure_time,
                    "estimated": estimated_time,
                    "delayed": delayed,
                    "coaches": coaches,
                    "platform": platform,
                    "cancelled": cancelled,
                }
            )

        print(trains)

    except Exception as e:
        print(f"ERROR; {e}")

    return trains


def format_time(iso_string):
    """'2026-08-04T11:00:00' -> '11:00'"""
    return datetime.fromisoformat(iso_string).strftime("%H:%M")


CARD_PADDING = 15  # TODO: tune - inner padding between card border and text

# Fonts for the card - split out so departure time can be bigger than the rest
FONT_TIME = "./resources/fonts/Roboto-Medium.ttf"


def draw_train_card(draw, box, train, font_time, font_dest, font_meta):
    # Draw a single rounded-rectangle card for one train.

    x0, y0, x1, y1 = box

    # Cancelled trains get a red outline, delayed get orange, on-time stay black
    if train["cancelled"]:
        outline_colour = "red"
    elif train["delayed"]:
        outline_colour = "orange"
    else:
        outline_colour = "black"

    draw.rounded_rectangle(
        box, radius=CARD_RADIUS, outline=outline_colour, width=2, fill="white"
    )

    pad = CARD_PADDING
    text_top = y0 + pad
    text_bottom = y1 - pad

    # --- Left block: big departure time (+ estimated time under it if delayed) ---
    departure_hm = format_time(train["departure"])
    time_x = x0 + pad
    draw.text((time_x, text_top), departure_hm, font=font_time, fill="black")

    if train["cancelled"]:
        status_text = "CANCELLED"
        status_colour = "red"
    elif train["delayed"]:
        status_text = f"Exp {format_time(train['estimated'])}"
        status_colour = "orange"
    else:
        status_text = "On time"
        status_colour = "black"

    time_bbox = draw.textbbox((time_x, text_top), departure_hm, font=font_time)
    draw.text(
        (time_x, time_bbox[3] + 2), status_text, font=font_meta, fill=status_colour
    )

    # --- Middle: destination ---
    dest_x = (
        x0 + (x1 - x0) // 2 - 40
    )  # TODO: tune - shift so it sits after the time block
    draw.text((dest_x, text_top), train["heading_to"], font=font_dest, fill="black")

    # --- Right block: platform / coaches, right-aligned ---
    meta_text = f"Plat {train['platform']}\n{train['coaches']} coaches"
    meta_bbox = draw.multiline_textbbox((0, 0), meta_text, font=font_meta)
    meta_width = meta_bbox[2] - meta_bbox[0]
    meta_x = x1 - pad - meta_width
    draw.multiline_text(
        (meta_x, text_top), meta_text, font=font_meta, fill="black", align="right"
    )


def draw_header(draw, img, display_width, from_name, to_name, font_header):
    """Draw the From (left) / logo (center) / To (right) band. Shared by the
    normal board and the no-trains fallback screen."""
    header_margin = 20
    from_bbox = draw.textbbox((0, 0), from_name, font=font_header)
    from_height = from_bbox[3] - from_bbox[1]
    from_y = (HEADER_HEIGHT - from_height) // 2
    draw.text((header_margin, from_y), from_name, font=font_header, fill="black")

    with Image.open(LOGO_PATH).convert("RGBA") as logo:
        logo_size = 64  # TODO: tune - native is 316x316
        logo = logo.resize((logo_size, logo_size))
        logo_x = (display_width - logo_size) // 2
        logo_y = (HEADER_HEIGHT - logo_size) // 2
        img.paste(logo, (logo_x, logo_y), logo)

    to_bbox = draw.textbbox((0, 0), to_name, font=font_header)
    to_width = to_bbox[2] - to_bbox[0]
    to_height = to_bbox[3] - to_bbox[1]
    to_x = display_width - header_margin - to_width
    to_y = (HEADER_HEIGHT - to_height) // 2
    draw.text((to_x, to_y), to_name, font=font_header, fill="black")


def draw_train_board(from_name, to_name, trains):
    """Render the full board: From / logo / To header, then up to 3 train cards."""
    inky = get_display()

    # Blank canvas - no pre-made background PNG for this one, unlike your other modules
    img = Image.new("RGB", inky.resolution, "white")
    draw = ImageDraw.Draw(img)
    display_width, display_height = img.size

    font_header = ImageFont.truetype(FONT_PATH, 28)  # From / To labels
    font_time = ImageFont.truetype(FONT_TIME, 32)  # big departure time on each card
    font_dest = ImageFont.truetype(FONT_PATH, 24)  # destination name on each card
    font_meta = ImageFont.truetype(FONT_PATH, 18)  # status / platform / coaches

    draw_header(draw, img, display_width, from_name, to_name, font_header)

    # --- Three cards below the header ---
    available_height = display_height - HEADER_HEIGHT
    card_height = (
        available_height - (CARD_GAP * 2)
    ) // 3  # TODO: sanity check this math

    for i, train in enumerate(trains[:3]):
        y0 = HEADER_HEIGHT + i * (card_height + CARD_GAP)
        y1 = y0 + card_height
        box = (CARD_MARGIN_X, y0, display_width - CARD_MARGIN_X, y1)
        draw_train_card(draw, box, train, font_time, font_dest, font_meta)

    inky.set_image(img)
    inky.show()


def draw_no_trains(from_name, to_name):
    """Fallback screen: still show the From / logo / To header so the board
    doesn't fail silently, with a message below instead of cards."""
    inky = get_display()

    img = Image.new("RGB", inky.resolution, "white")
    draw = ImageDraw.Draw(img)
    display_width, display_height = img.size

    font_header = ImageFont.truetype(FONT_PATH, 28)
    font_message = ImageFont.truetype(FONT_PATH, 24)

    draw_header(draw, img, display_width, from_name, to_name, font_header)

    message = "No trains to display"
    msg_bbox = draw.textbbox((0, 0), message, font=font_message)
    msg_width = msg_bbox[2] - msg_bbox[0]
    msg_height = msg_bbox[3] - msg_bbox[1]
    msg_x = (display_width - msg_width) // 2
    msg_y = HEADER_HEIGHT + (display_height - HEADER_HEIGHT - msg_height) // 2
    draw.text((msg_x, msg_y), message, font=font_message, fill="black")

    inky.set_image(img)
    inky.show()


if __name__ == "__main__":
    trains = get_timetable()

    if trains:
        draw_train_board(trains[0]["departing_from"], trains[0]["calling_at"], trains)
    else:
        draw_no_trains("Biggleswade", "St Pancras")
