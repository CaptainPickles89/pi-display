import os
import random
import time
import subprocess
import matplotlib.pyplot as plt
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

def load_api_key():
    # Path to your creds directory where the API key is stored
    api_key_path = './creds/alphavantage-api.txt'

    try:
        with open(api_key_path, 'r') as f:
            api_key = f.read().strip()  # Remove any surrounding whitespace
        return api_key
    except FileNotFoundError:
        print(f"Error: API key file not found at {api_key_path}")
        return None
    
def fetch_stock_data(symbol="IGG.L"):
    api_key = load_api_key()
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    
    if "Time Series (5min)" in data:
        # Fetch the most recent data (latest available)
        times = list(data['Time Series (5min)'].keys())
        latest_time = times[0]
        latest_data = data['Time Series (5min)'][latest_time]
        price = float(latest_data['4. close'])
        return price
    else:
        print("Error fetching stock data")
        return None

def plot_stock_graph(prices):
    fig, ax = plt.subplots(figsize=(5, 3))  # Adjust the size to fit the screen
    
    # Plot a simple line chart for the stock prices
    ax.plot(prices, color='blue', label="Stock Price")
    
    # Set labels and title
    ax.set_title("Stock Price Over Time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Price")
    
    # Save the plot as a PNG image in memory
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)
    buf.close()
    
    return img

def display_stock_graph(image):
    # Initialize the Inky display
    inky = auto()
    
    # Display the image (graph) on the Inky display
    inky.set_image(image)
    inky.show()

def fetch_opening_price(symbol="IGG.L"):
    api_key = load_api_key()
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    
    if "Time Series (Daily)" in data:
        latest_day = list(data['Time Series (Daily)'].keys())[0]
        opening_price = float(data['Time Series (Daily)'][latest_day]['1. open'])
        return opening_price
    else:
        print("Error fetching opening price")
        return None
    
def ig_stock():
    api_key = load_api_key()
    symbol = "IGG.L"  # The stock symbol you want to track
    
    while True:
        # Fetch current stock price
        current_price = fetch_stock_data(symbol, api_key)
        
        if current_price:
            # Fetch the opening price (for up/down comparison)
            opening_price = fetch_opening_price(symbol, api_key)
            
            if opening_price:
                # Compare and get the up/down status
                up_down_status = display_up_down_info(current_price, opening_price)
                print(up_down_status)  # Print to console or use Inky to show status
                
                # Generate the graph with the latest stock prices
                prices = [current_price]  # For simplicity, we only use the current price for now
                graph_image = plot_stock_graph(prices)
                
                # Display the graph on the Inky screen
                display_stock_graph(graph_image)
                
        # Wait for 5 minutes before refreshing the data
        time.sleep(300)  # 5 minutes    


def display_up_down_info(current_price, opening_price):
    # Check if the stock is up or down for the day
    if current_price > opening_price:
        return "Stock is UP today!"
    elif current_price < opening_price:
        return "Stock is DOWN today!"
    else:
        return "Stock price is the SAME today."


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
    display_functions = [lambda: display_image(random.choice(image_files)), ig_stock]
    
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
