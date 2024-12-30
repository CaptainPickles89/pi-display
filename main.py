import os
import random
import time
import subprocess
import warnings
import matplotlib.pyplot as plt
import yfinance as yf
import io
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from gpiozero import Button
from inky.auto import auto

# Initialize the Inky Impression
inky_display = auto()
inky_display.set_border(inky_display.WHITE)

# Button setup
button_a = Button(5)  # Adjust GPIO pin number if needed

# Paths
image_dir = "/home/danny/Pictures"  # Change to your image directory

def get_stock(symbol):
    try:
        subprocess.run(['python3', 'stocks.py', symbol])
        image_path="/tmp/stock_graph.png"
        print(f"Displaying stock graph from {image_path}")
        display_image(image_path)
        return 0  # success
    except Exception as e:
        print(f"Failed to get stock data for {symbol}: {e}")
        return 1  # failure

def show_pihole():
    try:
        subprocess.run(["python3", "pihole.py"])
        return 0  # success
    except Exception as e:
        print(f"Failed to get stock pihole data: {e}")
        return 1  # failure
    
def check_birthdays():
    try:
        subprocess.run(["python3", "birthdays.py", "./birthdays.json"])
        return 0  # success
    except Exception as e:
        print(f"Failed to get stock pihole data: {e}")
        return 1  # failure


# Clear the e-ink screen 
def screen_clear():
    try:
        subprocess.run(["python3", "clear.py"])
        return 0  # success
    except Exception as e:
        print(f"Failed to clear display: {e}")
        return 1  # failure

# Display an image
def display_image(image_path):
    try:
        print(f"Now loading {image_path} to display")
        subprocess.run(['python3', 'image.py', image_path])
    except Exception as e:
        print(f"Failed to display image: {e}")


# Main loop
def main():
    image_files = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    display_functions = [lambda: show_pihole(), lambda: display_image(random.choice(image_files)), lambda: get_stock("IGG.L"),]
    
    current_index = 0

    while True:
        print(f"Calling index {current_index}")
        print(f"Display function {display_functions[current_index]}")
        if display_functions[current_index]:
           display_functions[current_index]()
        else:
           print(f"Error: Function at index {current_index} is None")
        
        # Wait for 10 minutes or button press
        start_time = time.time()
        while time.time() - start_time < 600:  # 10 minutes
            if button_a.is_pressed:
                break
            time.sleep(0.1)  # Check button press every 100ms

        current_index = (current_index + 1) % len(display_functions)

if __name__ == "__main__":
    main()
