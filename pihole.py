import requests
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto

def fetch_pihole_stats():
    api_url = "http://192.168.7.213/"
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

        print(f"Pihole stats returned {percentage_blocked} blocked so far today")

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
    img = Image.new("P", inky.resolution)
    draw = ImageDraw.Draw(img)

    # Font settings (update path to your font file)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, 20)

    # Display the stats
    draw.text((10, 10), "Pi-hole Stats:", font=font, fill=inky.BLACK)
    draw.text((10, 40), f"Ads Blocked: {stats['ads_blocked']}", font=font, fill=inky.RED)
    draw.text((10, 70), f"DNS Queries: {stats['dns_queries']}", font=font, fill=inky.BLACK)
    draw.text((10, 100), f"% Blocked: {stats['percentage_blocked']}%", font=font, fill=inky.BLACK)

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

