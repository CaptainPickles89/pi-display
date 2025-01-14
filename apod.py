import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from io import BytesIO
from inky.auto import auto

def load_api_key():
    # Path to your creds directory where the API key is stored
    api_key_path = './creds/apod-api.txt'

    try:
        with open(api_key_path, 'r') as f:
            api_key = f.read().strip()  # Remove any surrounding whitespace
        return api_key
    except FileNotFoundError:
        print(f"Error: API key file not found at {api_key_path}")
        return None

def fetch_apod():
    # Grab API Key
    api_key = load_api_key()

    # Fetch the Astronomy Picture of the Day (APOD) from NASA API.
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Check if the APOD has an image
        if data["media_type"] != "image":
            print("APOD is not an image today.")
            return None
        
        # Fetch the image
        image_url = data["url"]
        image_title = data["title"]
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        
        # Open the image
        image = Image.open(BytesIO(image_response.content))
        return image, image_title

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch APOD: {e}")
        return None

def display_apod():

    # Fetch and display the APOD image on the Inky display.

    inky_display = auto()
    inky_display.set_border(inky_display.BLACK)

    apod_image, apod_title = fetch_apod()
    if apod_image:
        print(f"NASA Image of the day displaying now!")
        # Resize image to fit the Inky display
        apod_image = apod_image.resize(inky_display.resolution)
        # Get the resolution of the Inky display dynamically
        display_width, display_height = apod_image.size  # Assuming image is already resized to fit display
        draw = ImageDraw.Draw(apod_image)
        # Font settings (update path to your font file)
        font_path = "./resources/fonts/Roboto-Regular.ttf"
        title_font = ImageFont.truetype(font_path, 25)
        # Get text size to calculate bottom-right position
        text_width, text_height = draw.textsize(apod_title, font=title_font)
        x_position = display_width - text_width - 10  # 10px padding from the right
        y_position = display_height - text_height - 10  # 10px padding from the bottom
        draw.text((x_position, y_position), apod_title, font=title_font, fill="black", stroke_width=2, stroke_fill="white")
        # Brighten the image slightly
        enhancer = ImageEnhance.Brightness(apod_image)
        apod_image = enhancer.enhance(1.5)
        inky_display.set_image(apod_image)
        inky_display.show()
    else:
        print("No APOD image to display.")

if __name__ == "__main__":
    display_apod()
