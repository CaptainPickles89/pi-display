import requests
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto

def fetch_pihole_stats():
    api_url = "http://192.168.7.213/admin"
    api_key = load_api_key()
    try:
        # Build the API URL
        url = f"{api_url}/api.php"
        params = {"summary": True}
        if api_key:
            params["auth"] = api_key

        # Fetch the stats
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract the stats
        ads_blocked_today = data.get("ads_blocked_today", "N/A")
        dns_queries_today = data.get("dns_queries_today", "N/A")
        percentage_blocked = data.get("ads_percentage_today", "N/A")

        print(f"Pihole stats returned {percentage_blocked}% blocked so far today")

        return {
            "ads_blocked": ads_blocked_today,
            "dns_queries": dns_queries_today,
            "percentage_blocked": percentage_blocked,
        }

    except Exception as e:
        print(f"Failed to fetch Pi-hole stats: {e}")
        return None
    
def load_api_key():
    # Path to your creds directory where the API key is stored
    api_key_path = './creds/pihole-api.txt'

    try:
        with open(api_key_path, 'r') as f:
            api_key = f.read().strip()  # Remove any surrounding whitespace
        return api_key
    except FileNotFoundError:
        print(f"Error: API key file not found at {api_key_path}")
        return None

def display_pihole_stats(stats):
    # Prepare the display
    inky = auto()
    img = Image.open("./resources/imgs/pihole-bg1-01.png").convert("P")  # Convert to mode "P" for Inky compatibility
    draw = ImageDraw.Draw(img)

    # Font settings (update path to your font file)
    font_path = "/usr/share/fonts/truetype/roboto/unhinted/RobotoCondensed-Medium.ttf"
    font = ImageFont.truetype(font_path, 50)

    # Format the stats into a single block of text
    stats_text = (
        "Pi-hole Stats:\n"
        f"Ads Blocked: {stats['ads_blocked']}\n"
        f"DNS Queries: {stats['dns_queries']}\n"
        f"Blocked: {stats['percentage_blocked']}%"
    )

# Calculate vertical centering
    total_height = sum(draw.textsize(line, font=font)[1] for line in stats_text) + (len(stats_text) - 1) * 10  # Add line spacing
    image_width, image_height = img.size
    y_position = (image_height - total_height) // 2

    # Draw each line, centered horizontally
    for line in stats_text:
        line_width, line_height = draw.textsize(line, font=font)
        x_position = (image_width - line_width) // 2
        draw.text((x_position, y_position), line, font=font, fill=0)  # Black text
        y_position += line_height + 10  # Move down for the next line (10px line spacing)

    # Draw the text on the image
    draw.multiline_text((x_position, y_position), stats_text, font=font, fill=0)  # 0 for black text

    # Debug: Save the image to check the output
    img.save("/tmp/debug_output.png")

    # Show on the Inky
    inky.set_image(img)
    inky.show()

def show_pihole_stats():

    stats = fetch_pihole_stats()
    if stats:
        display_pihole_stats(stats)
        return
    else:
        print("Failed to display Pi-hole stats.")
        return None

if __name__ == "__main__":
    show_pihole_stats()

