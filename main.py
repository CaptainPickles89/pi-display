import os
import random
import time
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto
from gpiozero import Button
import requests

# Initialize the Inky Impression
inky_display = auto()
inky_display.set_border(inky_display.WHITE)

# Button setup
button_a = Button(5)  # Adjust GPIO pin number if needed

# Paths
image_dir = "/home/danny/Pictures"  # Change to your image directory

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
        return f"{weather['temperature']}°C, {weather['weathercode']} ({weather['windspeed']} km/h wind)"
    except Exception as e:
        return f"Error fetching weather: {e}"

# Display an image
def display_image(image_path):
    try:
        img = Image.open(image_path)
        inky_display.set_image(img)
        inky_display.show()
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
    display_functions = [lambda: display_image(random.choice(image_files)), display_weather]
    
    current_index = 0

    while True:
        # Display current item
        display_functions[current_index]()
        
        # Wait for 10 minutes or button press
        start_time = time.time()
        while time.time() - start_time < 600:  # 10 minutes
            if button_a.is_pressed:
                current_index = (current_index + 1) % len(display_functions)
                break
            time.sleep(0.1)  # Check button press every 100ms

if __name__ == "__main__":
    main()
