import math
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

# Colors (Inky Impression supports black, white, red, yellow, green, blue, orange)
C_SUN = (220, 170, 0)
C_SUN_OUTLINE = (180, 120, 0)
C_CLOUD_FILL = (180, 180, 180)
C_CLOUD_OUT = (60, 60, 60)
C_RAIN = (0, 80, 200)
C_SNOW = (80, 130, 220)
C_LIGHTNING = (220, 170, 0)
C_FOG = (120, 120, 120)
C_BLACK = (0, 0, 0)


# --- Icon drawing primitives ---

def _sun(draw, cx, cy, size):
    lw = max(2, size // 16)
    r = size // 4
    ray_in = int(size * 0.33)
    ray_out = int(size * 0.48)
    for i in range(8):
        a = i * math.pi / 4
        draw.line(
            [cx + int(ray_in * math.cos(a)), cy + int(ray_in * math.sin(a)),
             cx + int(ray_out * math.cos(a)), cy + int(ray_out * math.sin(a))],
            fill=C_SUN, width=lw,
        )
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 fill=C_SUN, outline=C_SUN_OUTLINE, width=lw)


def _cloud(draw, cx, cy, size):
    lw = max(1, size // 22)
    bw = int(size * 0.74)
    bh = int(size * 0.28)
    bx1, bx2 = cx - bw // 2, cx + bw // 2
    by1, by2 = cy - bh // 4, cy + bh * 3 // 4
    bumps = [
        (cx - bw // 4, by1 - int(size * 0.09), int(size * 0.17)),
        (cx,           by1 - int(size * 0.17), int(size * 0.22)),
        (cx + bw // 4, by1 - int(size * 0.07), int(size * 0.16)),
    ]
    for bx, sby, br in bumps:
        draw.ellipse([bx - br, sby - br, bx + br, sby + br], fill=C_CLOUD_FILL)
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=bh // 3, fill=C_CLOUD_FILL)
    for bx, sby, br in bumps:
        draw.ellipse([bx - br, sby - br, bx + br, sby + br],
                     outline=C_CLOUD_OUT, width=lw)
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=bh // 3,
                            outline=C_CLOUD_OUT, width=lw)


def _rain_drops(draw, cx, cy, size, count=3):
    dr = max(2, size // 14)
    gap = int(size * 0.22)
    sx = cx - gap * (count - 1) // 2
    for i in range(count):
        dx = sx + i * gap
        draw.ellipse([dx - dr, cy - dr, dx + dr, cy + dr], fill=C_RAIN)


def _snow_flakes(draw, cx, cy, size, count=3):
    lw = max(1, size // 18)
    r = max(3, size // 9)
    gap = int(size * 0.22)
    sx = cx - gap * (count - 1) // 2
    for i in range(count):
        fx = sx + i * gap
        for a in [0, math.pi / 3, 2 * math.pi / 3]:
            draw.line(
                [fx + int(r * math.cos(a)), cy + int(r * math.sin(a)),
                 fx - int(r * math.cos(a)), cy - int(r * math.sin(a))],
                fill=C_SNOW, width=lw,
            )


def _lightning(draw, cx, cy, size):
    lw = max(2, size // 12)
    pts = [
        (cx + int(size * 0.10), cy - int(size * 0.22)),
        (cx - int(size * 0.06), cy + int(size * 0.02)),
        (cx + int(size * 0.04), cy + int(size * 0.02)),
        (cx - int(size * 0.10), cy + int(size * 0.24)),
    ]
    draw.line(pts, fill=C_LIGHTNING, width=lw)


def _fog_lines(draw, cx, cy, size):
    lw = max(2, size // 14)
    hw = int(size * 0.40)
    sp = int(size * 0.15)
    for i in range(-1, 2):
        y = cy + i * sp
        draw.line([cx - hw, y, cx + hw, y], fill=C_FOG, width=lw)


def _icon_group(code):
    if code == 0:
        return "sun"
    if code in (1, 2):
        return "sun_cloud"
    if code == 3:
        return "cloud"
    if code in (45, 48):
        return "fog"
    if code in (51, 53, 55, 61, 63, 65, 80, 81, 82):
        return "rain"
    if code in (71, 73, 75, 77, 85, 86):
        return "snow"
    if code in (95, 96, 99):
        return "storm"
    return "cloud"


def draw_icon(draw, cx, cy, size, code):
    group = _icon_group(code)
    cloud_cy = cy + int(size * 0.05)
    precip_cy = cy + int(size * 0.38)

    if group == "sun":
        _sun(draw, cx, cy, size)
    elif group == "sun_cloud":
        _sun(draw, cx + int(size * 0.18), cy - int(size * 0.18), int(size * 0.72))
        _cloud(draw, cx - int(size * 0.06), cy + int(size * 0.12), int(size * 0.78))
    elif group == "cloud":
        _cloud(draw, cx, cy, size)
    elif group == "fog":
        _fog_lines(draw, cx, cy, size)
    elif group == "rain":
        _cloud(draw, cx, cloud_cy, size)
        _rain_drops(draw, cx, precip_cy, size)
    elif group == "snow":
        _cloud(draw, cx, cloud_cy, size)
        _snow_flakes(draw, cx, precip_cy, size)
    elif group == "storm":
        _cloud(draw, cx, cloud_cy, size)
        _lightning(draw, cx, precip_cy, size)


# --- Data fetch ---

def fetch_weather(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,weathercode,windspeed_10m,precipitation"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode,sunrise,sunset"
        "&timezone=auto&forecast_days=4"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


# --- Display ---

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
        font_temp_hdr = ImageFont.truetype(FONT_PATH, 36)
        font_info_label = ImageFont.truetype(FONT_PATH, 22)
        font_info_val = ImageFont.truetype(FONT_PATH, 30)
        font_condition = ImageFont.truetype(FONT_PATH, 32)
        font_day = ImageFont.truetype(FONT_PATH, 23)
        font_hilo = ImageFont.truetype(FONT_PATH, 24)
        font_rain = ImageFont.truetype(FONT_PATH, 20)

        current = data["current"]
        daily = data["daily"]

        temp_c = round(current["temperature_2m"])
        code = current["weathercode"]
        wind = round(current["windspeed_10m"])
        precip = current["precipitation"]
        condition = WMO_CODES.get(code, "Unknown")
        hi_today = round(daily["temperature_2m_max"][0])
        lo_today = round(daily["temperature_2m_min"][0])

        def parse_time(dt_str):
            return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M").strftime("%H:%M")

        sunrise = parse_time(daily["sunrise"][0])
        sunset = parse_time(daily["sunset"][0])

        def col_centered_text(text, font, y, col_mid, fill=C_BLACK):
            b = draw.textbbox((0, 0), text, font=font)
            x = col_mid - (b[2] - b[0]) // 2
            draw.text((x, y), text, font=font, fill=fill)

        # ── Header ──────────────────────────────────────────────────
        draw.text((20, 14), "Weather", font=font_header, fill=C_BLACK)
        temp_str = f"{temp_c}°C"
        tb = draw.textbbox((0, 0), temp_str, font=font_temp_hdr)
        draw.text((width - (tb[2] - tb[0]) - 20, 12), temp_str,
                  font=font_temp_hdr, fill=C_BLACK)
        draw.line([(20, 58), (width - 20, 58)], fill=C_BLACK, width=2)

        # ── Main section: icon left, info right ──────────────────────
        icon_cx = 148
        icon_cy = 188
        draw_icon(draw, icon_cx, icon_cy, 200, code)

        # Vertical divider between icon and info panel
        draw.line([(296, 64), (296, 318)], fill=C_BLACK, width=1)

        # Info panel — right side starting at x=310
        info_x = 310
        info_x2 = 455  # second column for paired rows
        grey = (100, 100, 100)

        def info_row(label, value, x, y):
            draw.text((x, y), label, font=font_info_label, fill=grey)
            draw.text((x, y + 22), value, font=font_info_val, fill=C_BLACK)

        row_y = 66

        # Condition — full width, no label
        draw.text((info_x, row_y), condition, font=font_condition, fill=C_BLACK)
        row_y += 42

        # High / Low — full width
        info_row("High / Low", f"{hi_today}° / {lo_today}°", info_x, row_y)
        row_y += 58

        # Wind + Rain — side by side
        info_row("Wind", f"{wind} km/h", info_x, row_y)
        info_row("Rain", f"{precip} mm", info_x2, row_y)
        row_y += 58

        # Sunrise + Sunset — side by side
        info_row("Sunrise", sunrise, info_x, row_y)
        info_row("Sunset", sunset, info_x2, row_y)

        # ── Forecast strip ───────────────────────────────────────────
        draw.line([(20, 322), (width - 20, 322)], fill=C_BLACK, width=2)

        col_w = width // 3
        for i in range(1, 4):
            date_str = daily["time"][i]
            day_name = DAY_NAMES[datetime.strptime(date_str, "%Y-%m-%d").weekday()]
            hi = round(daily["temperature_2m_max"][i])
            lo = round(daily["temperature_2m_min"][i])
            rain_pct = daily["precipitation_probability_max"][i]
            day_code = daily["weathercode"][i]

            col_x = (i - 1) * col_w
            mid = col_x + col_w // 2

            col_centered_text(day_name, font_day, 326, mid)
            # Icon left of centre, temp right of icon — same line
            icon_x = col_x + 62
            temp_x = col_x + 120
            draw_icon(draw, icon_x, 378, 52, day_code)
            draw.text((temp_x, 362), f"{hi}°", font=font_hilo, fill=C_BLACK)

            if i < 3:
                draw.line([(col_x + col_w, 324), (col_x + col_w, height - 8)],
                          fill=C_BLACK, width=1)

        inky.set_image(image)
        inky.show()

    except Exception as e:
        print(f"Weather: render failed: {e}")


if __name__ == "__main__":
    display_weather()
