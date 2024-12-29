import os
import random
import time
import subprocess
import matplotlib.pyplot as plt
import yfinance as yf
import io
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from gpiozero import Button
import requests
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
    except Exception as e:
        print(f"Failed to get stock data for {symbol}: {e}")

def show_pihole():
    try:
        subprocess.run(["python3", "pihole.py"])
    except Exception as e:
        print(f"Failed to get stock pihole data: {e}")


# Bedfordshire weather API setup (use OpenWeatherMap as an alternative source)
def fetch_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 52.135,  # Approx Bedfordshire latitude
            "longitude": -0.468,  # Approx Bedfordshire longitude
            "current_weather": True,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        weather = data["current_weather"]
        print(f"Weather returned: {weather.temperature}")
        return f"{weather['temperature']}°C, {weather['weathercode']} ({weather['windspeed']} km/h wind)"
    except Exception as e:
        return f"Error fetching weather: {e}"

# Display an image
def display_image(image_path):
    try:
        print(f"Now loading {image_path} to display")
        subprocess.run(['python3', 'image.py', image_path])
    except Exception as e:
        print(f"Failed to display image: {e}")

# Display weather information
def display_weather():
    try:
        weather_info = fetch_weather()
        img = Image.new("P", inky_display.resolution)
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()  # Replace with a custom font if desired
        draw.text((10, 10), weather_info, inky_display.BLACK, font=font)
        inky_display.set_image(img)
        inky_display.show()
    except Exception as e:
        print(f"Failed to display weather: {e}")


# Main loop
def main():
    image_files = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    display_functions = [show_pihole(), lambda: display_image(random.choice(image_files)), lambda: get_stock("IGG.L"),]
    
    current_index = 0

    while True:
        # Check if the function is callable (i.e., not None)
        if display_functions[current_index]:
           display_functions[current_index]()
        else:
           print(f"Error: Function at index {current_index} is None")
        
        # Wait for 10 minutes or button press
        start_time = time.time()
        while time.time() - start_time < 600:  # 10 minutes
            if button_a.is_pressed:
                current_index = (current_index + 1) % len(display_functions)
                break
            time.sleep(0.1)  # Check button press every 100ms

if __name__ == "__main__":
    main()
