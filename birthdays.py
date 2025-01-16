#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto

def read_birthdays(file_path):
    try:
        with open(file_path, "r") as file:
            birthdays = json.load(file)  # Parse JSON into a Python dictionary
        return birthdays
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {}
    except Exception as e:
        print(f"Error loading birthdays: {e}")
        return {}

def check_birthdays():

    # Check if today is anyone's birthday    
    today = datetime.today()
    today_day_month = today.strftime('%d-%m')  # Get current day and month in 'DD-MM' format
    birthdays = read_birthdays("./birthdays.json")

    # Collect all matches for today's date
    birthday_matches = [name for name, birthdate in birthdays.items() if birthdate.startswith(today_day_month)]

    if birthday_matches:
        print("There are birthdays today!")
        inky = auto()
        img = Image.open("./resources/imgs/birthday-bg1-01.png")
        draw = ImageDraw.Draw(img)
            
        # Font settings (update path to your font file)
        font_path = "./resources/fonts/Roboto-Medium.ttf"
        font = ImageFont.truetype(font_path, 50)

        # Birthday message for the inky
        names = "\n".join(birthday_matches)
        message = f"Birthdays Today!\n{names}"

        # Measure text size
        text_bbox = draw.multiline_textbbox((0, 0), message, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Calculate position to center the text
        image_width, image_height = img.size
        x_position = (image_width - text_width) // 2
        y_position = (image_height - text_height) // 2

        # Draw the text on the image
        draw.multiline_text((x_position, y_position), message, font=font, align='center', fill=0)  # Black text
        # Show on the Inky
        inky.set_image(img)
        inky.show()
        return birthday_matches  # Return the list of names for further use if needed
    else:
        print("No birthdays today.")
        return None

if __name__ == "__main__":
    check_birthdays()
