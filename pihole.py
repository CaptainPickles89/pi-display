import requests
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto


def get_sid(api_url, password):
    resp = requests.post(f"{api_url}/api/auth", json={"password": password})
    resp.raise_for_status()
    data = resp.json()
    return data["session"]["sid"]


def fetch_pihole_stats(api_url, password):
    try:
        sid = get_sid(api_url, password)
        headers = {"X-FTL-SID": sid}

        stats_url = f"{api_url}/api/stats/summary"
        response = requests.get(stats_url, headers=headers)
        response.raise_for_status()

        data = response.json()

        return {
            "ads_blocked": data.get("queries", {}).get("blocked", "N/A"),
            "dns_queries": data.get("queries", {}).get("total", "N/A"),
            "percentage_blocked": round(
                data.get("queries", {}).get("percent_blocked", 0), 2
            ),
            "unique_clients": data.get("clients", {}).get("active", "N/A"),
            "domains_blocked": data.get("gravity", {}).get(
                "domains_being_blocked", "N/A"
            ),
        }

    except Exception as e:
        print(f"Failed to fetch Pi-hole stats: {e}")
        return None


def load_password():
    password_path = "./creds/pihole-api.txt"
    try:
        with open(password_path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: Password file not found at {password_path}")
        return None


def display_pihole_stats(stats):
    inky = auto()
    with Image.open("./resources/imgs/pihole-bg1-01.png") as img:
        draw = ImageDraw.Draw(img)

        font_path = "./resources/fonts/Roboto-Medium.ttf"
        font = ImageFont.truetype(font_path, 45)

        stats_text = (
            f"Unique Clients: {stats['unique_clients']}\n"
            f"Ads Blocked: {stats['ads_blocked']}\n"
            f"DNS Queries: {stats['dns_queries']}\n"
            f"Domains Blocked: {stats['domains_blocked']}\n"
            f"Blocked: {stats['percentage_blocked']}%"
        )

        text_bbox = draw.multiline_textbbox((0, 0), stats_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        image_width, image_height = img.size
        x_position = (image_width - text_width) // 2
        y_position = (image_height - text_height) // 2

        draw.multiline_text(
            (x_position, y_position), stats_text, font=font, align="center", fill=0
        )

        inky.set_image(img)
        inky.show()


def show_pihole_stats():
    api_url = "http://192.168.7.213"
    password = load_password()

    if not password:
        print("Pi-hole password missing. Exiting.")
        return

    stats = fetch_pihole_stats(api_url, password)

    if stats:
        display_pihole_stats(stats)
    else:
        print("Failed to display Pi-hole stats.")


if __name__ == "__main__":
    show_pihole_stats()
