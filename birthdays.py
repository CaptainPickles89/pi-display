#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import warnings
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto

def read_birthdays(file_path: str) -> dict:
    """
    Read birthdays from a JSON file and return as a dictionary.
    
    Args:
        file_path (str): Path to the JSON file containing the birthdays.
        
    Returns:
        dict: A dictionary with names as keys and birthdates as values.
    """
    try:
        with open(file_path, 'r') as file:
            birthdays = json.load(file)
        check_birthdays(birthdays)
        return birthdays
    except Exception as e:
        print(f"Error reading the file: {e}")
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
                print(f"Happy Birthday, {name}!")
                inky = auto()
                img = Image.open("./resources/imgs/pihole-bg1-01.png").convert("P")  # Convert to mode "P" for Inky compatibility
                draw = ImageDraw.Draw(img)
                    
                # Font settings (update path to your font file)
                font_path = "./resources/fonts/Roboto-Medium.ttf"
                font = ImageFont.truetype(font_path, 50)

                # Birthday message
                message = (f"It's {name}'s Birthday today!")

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
        print("No image path provided!")
