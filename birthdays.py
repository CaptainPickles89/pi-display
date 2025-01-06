#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import warnings
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto

def read_birthdays(file_path):
    try:
        with open(file_path, "r") as file:
            birthdays = json.load(file)  # Parse JSON into a Python dictionary
            check_birthdays(birthdays)
        return birthdays
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {}
    except Exception as e:
        print(f"Error loading birthdays: {e}")
        return {}

def check_birthdays(birthdays: dict) -> None:
    """
    Check if today is anyone's birthday from the given list.
    
    Args:
        birthdays (dict): A dictionary with names as keys and birthdates as values in 'DD-MM-YYYY' format.
    """
    today = datetime.today()
    today_day_month = today.strftime('%d-%m')  # Get current day and month in 'DD-MM' format
    
    for name, birthdate in birthdays.items():
        birth_day_month = birthdate.split("-")[:2]  # Extract only the 'DD-MM' part of the birthdate
        if today_day_month == '-'.join(birth_day_month):  # Check if today matches the birthday's day and month
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="Busy Wait: Held high")
                print(f"It looks like it's {name}'s birthday today!")
                inky = auto()
                img = Image.open("./resources/imgs/birthday-bg1-01.png").convert("P")  # Convert to mode "P" for Inky compatibility
                draw = ImageDraw.Draw(img)
                    
                # Font settings (update path to your font file)
                font_path = "./resources/fonts/Roboto-Medium.ttf"
                font = ImageFont.truetype(font_path, 50)

                # Birthday message
                message = (f"Happy Birthday {name}!")

                # Measure text size
                text_bbox = draw.multiline_textbbox((0, 0), message, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]

                # Calculate position to center the text
                image_width, image_height = img.size
                x_position = (image_width - text_width) // 2
                y_position = (image_height - text_height) // 2

                # Draw the text on the image
                draw.multiline_text((x_position, y_position), message, font=font, fill=0)  # Black text
                # Show on the Inky
                inky.set_image(img)
                inky.show()
        else:
            print(f"it's not {name}'s today")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]  # Get the file path from the command-line argument
        read_birthdays(file_path)
    else:
        print("No Birthdays provided!")
