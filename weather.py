import requests
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto
from datetime import datetime

FONT_PATH = "./resources/fonts/Roboto-Medium.ttf"
CREDS_PATH = "./creds/weather-location.txt"

WMO_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Icy Fog",
    51: "Light Drizzle",
    53: "Drizzle",
    55: "Heavy Drizzle",
    61: "Light Rain",
    63: "Rain",
    65: "Heavy Rain",
    71: "Light Snow",
    73: "Snow",
    75: "Heavy Snow",
    77: "Snow Grains",
    80: "Light Showers",
    81: "Showers",
    82: "Heavy Showers",
    85: "Snow Showers",
    86: "Heavy Snow Showers",
    95: "Thunderstorm",
    96: "Thunderstorm + Hail",
    99: "Thunderstorm + Hail",
}

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_weather(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,weathercode,windspeed_10m,precipitation"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode"
        "&timezone=auto&forecast_days=4"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def display_weather():
    try:
        with open(CREDS_PATH) as f:
            lat, lon = f.read().strip().split(",")
    except Exception as e:
        print(f"Weather: failed to read location: {e}")
        return

    try:
        data = fetch_weather(lat.strip(), lon.strip())
    except Exception as e:
        print(f"Weather: fetch failed: {e}")
        return

    try:
        inky = auto()
        width, height = inky.resolution

        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        font_header = ImageFont.truetype(FONT_PATH, 32)
        font_temp = ImageFont.truetype(FONT_PATH, 88)
        font_condition = ImageFont.truetype(FONT_PATH, 38)
        font_detail = ImageFont.truetype(FONT_PATH, 28)
        font_day_label = ImageFont.truetype(FONT_PATH, 26)
        font_day_val = ImageFont.truetype(FONT_PATH, 30)

        current = data["current"]
        daily = data["daily"]

        temp_c = round(current["temperature_2m"])
        code = current["weathercode"]
        wind = round(current["windspeed_10m"])
        precip = current["precipitation"]
        condition = WMO_CODES.get(code, "Unknown")

        # Header
        draw.text((20, 16), "Weather", font=font_header, fill="black")
        now_str = datetime.now().strftime("%H:%M")
        draw.text((width - 90, 16), now_str, font=font_header, fill="black")

        # Current temp — centered
        temp_str = f"{temp_c}°C"
        bbox = draw.textbbox((0, 0), temp_str, font=font_temp)
        tx = (width - (bbox[2] - bbox[0])) // 2
        draw.text((tx, 55), temp_str, font=font_temp, fill="black")

        # Condition — centered
        bbox = draw.textbbox((0, 0), condition, font=font_condition)
        cx = (width - (bbox[2] - bbox[0])) // 2
        draw.text((cx, 175), condition, font=font_condition, fill="black")

        # Wind + precip row — centered
        detail_str = f"Wind: {wind} km/h    Rain: {precip} mm"
        bbox = draw.textbbox((0, 0), detail_str, font=font_detail)
        dx = (width - (bbox[2] - bbox[0])) // 2
        draw.text((dx, 228), detail_str, font=font_detail, fill="black")

        # Divider
        draw.line([(20, 272), (width - 20, 272)], fill="black", width=2)

        # 3-day forecast (daily[0] is today, show +1, +2, +3)
        col_w = width // 3
        for i in range(1, 4):
            date_str = daily["time"][i]
            day_name = DAY_NAMES[datetime.strptime(date_str, "%Y-%m-%d").weekday()]
            hi = round(daily["temperature_2m_max"][i])
            lo = round(daily["temperature_2m_min"][i])
            rain_pct = daily["precipitation_probability_max"][i]
            day_code = daily["weathercode"][i]
            day_cond = WMO_CODES.get(day_code, "")
            # Truncate long condition names
            if len(day_cond) > 13:
                day_cond = day_cond[:12] + "."

            col_x = (i - 1) * col_w
            mid_x = col_x + col_w // 2

            def centered(text, font, y):
                b = draw.textbbox((0, 0), text, font=font)
                x = mid_x - (b[2] - b[0]) // 2
                draw.text((x, y), text, font=font, fill="black")

            centered(day_name, font_day_label, 284)
            centered(day_cond, font_day_label, 314)
            centered(f"{hi}° / {lo}°", font_day_val, 350)
            centered(f"Rain: {rain_pct}%", font_day_label, 392)

            # Column dividers
            if i < 3:
                draw.line([(col_x + col_w, 280), (col_x + col_w, height - 10)], fill="black", width=1)

        inky.set_image(image)
        inky.show()

    except Exception as e:
        print(f"Weather: render failed: {e}")


if __name__ == "__main__":
    display_weather()
