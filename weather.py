import json
import math
import os
import requests
from PIL import Image, ImageDraw, ImageFont
from display import get_display
from datetime import datetime, timezone, timedelta

FONT_PATH = "./resources/fonts/Roboto-Medium.ttf"
CREDS_PATH = "./creds/weather-location.txt"
API_KEY_PATH = "./creds/metoffice-api.txt"
CACHE_FILE = "/tmp/weather_cache.json"
CACHE_TTL_HOURS = 3

HOURLY_URL = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/hourly"
SUNRISE_URL = "https://api.sunrise-sunset.org/json"

MET_CODES = {
    0:  "Clear Night",
    1:  "Sunny",
    2:  "Partly Cloudy",
    3:  "Partly Cloudy",
    5:  "Mist",
    6:  "Fog",
    7:  "Cloudy",
    8:  "Overcast",
    9:  "Light Shower",
    10: "Light Shower",
    11: "Drizzle",
    12: "Light Rain",
    13: "Heavy Shower",
    14: "Heavy Shower",
    15: "Heavy Rain",
    16: "Sleet Shower",
    17: "Sleet Shower",
    18: "Sleet",
    19: "Hail Shower",
    20: "Hail Shower",
    21: "Hail",
    22: "Snow Shower",
    23: "Snow Shower",
    24: "Light Snow",
    25: "Heavy Snow Shower",
    26: "Heavy Snow Shower",
    27: "Heavy Snow",
    28: "Thunder Shower",
    29: "Thunder Shower",
    30: "Thunder",
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
    if code in (0, 1):
        return "sun"
    if code in (2, 3):
        return "sun_cloud"
    if code in (5, 6):
        return "fog"
    if code in (7, 8):
        return "cloud"
    if 9 <= code <= 21:
        return "rain"
    if code in (22, 23, 24, 25, 26, 27):
        return "snow"
    if code in (28, 29, 30):
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


# --- Helpers ---

def _get_current_hourly(time_series):
    now = datetime.now(timezone.utc)
    current = time_series[0]
    for entry in time_series:
        t = datetime.fromisoformat(entry["time"].replace("Z", "+00:00"))
        if t <= now:
            current = entry
        else:
            break
    return current


def _parse_utc(dt_str):
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    return dt.astimezone().strftime("%H:%M")


def _group_by_date(time_series):
    groups = {}
    for entry in time_series:
        d = entry["time"][:10]
        groups.setdefault(d, []).append(entry)
    return groups


def _day_summary(date_str, entries):
    temps = [e["screenTemperature"] for e in entries if "screenTemperature" in e]
    noon = next((e for e in entries if "T12:" in e["time"]),
                entries[len(entries) // 2])
    return {
        "date": date_str,
        "maxTemp": max(temps) if temps else 0,
        "minTemp": min(temps) if temps else 0,
        "code": noon.get("significantWeatherCode", 7),
    }


# --- Cache ---

def _load_cache():
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE) as f:
            cache = json.load(f)
        fetched_at = datetime.fromisoformat(cache["fetched_at"])
        if datetime.now(timezone.utc) - fetched_at < timedelta(hours=CACHE_TTL_HOURS):
            return cache["hourly_ts"], cache["sun"]
    except Exception:
        pass
    return None


def _save_cache(hourly_ts, sun):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump({
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "hourly_ts": hourly_ts,
                "sun": sun,
            }, f)
    except Exception:
        pass


# --- Data fetch ---

def fetch_weather(lat, lon, api_key):
    cached = _load_cache()
    if cached:
        return cached

    headers = {"apikey": api_key, "accept": "application/json"}
    params = {"latitude": lat, "longitude": lon, "includeLocationName": "false"}
    hourly_resp = requests.get(HOURLY_URL, headers=headers, params=params, timeout=10)
    hourly_resp.raise_for_status()
    hourly_ts = hourly_resp.json()["features"][0]["properties"]["timeSeries"]

    sun = {"sunrise": "N/A", "sunset": "N/A"}
    try:
        sr = requests.get(SUNRISE_URL,
                          params={"lat": lat, "lng": lon, "formatted": 0},
                          timeout=5)
        if sr.ok:
            r = sr.json()["results"]
            sun = {
                "sunrise": _parse_utc(r["sunrise"]),
                "sunset": _parse_utc(r["sunset"]),
            }
    except Exception:
        pass

    _save_cache(hourly_ts, sun)
    return hourly_ts, sun


# --- Display ---

def display_weather():
    try:
        with open(CREDS_PATH) as f:
            lat, lon = f.read().strip().split(",")
        with open(API_KEY_PATH) as f:
            api_key = f.read().strip()
    except Exception as e:
        print(f"Weather: failed to read credentials: {e}")
        return

    try:
        hourly_ts, sun = fetch_weather(lat.strip(), lon.strip(), api_key)
    except Exception as e:
        print(f"Weather: fetch failed: {e}")
        return

    try:
        inky = get_display()
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

        grey = (100, 100, 100)

        current = _get_current_hourly(hourly_ts)
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        groups = _group_by_date(hourly_ts)

        today_temps = [e["screenTemperature"] for e in groups.get(today_str, [])
                       if "screenTemperature" in e]
        hi_today = round(max(today_temps)) if today_temps else round(current["screenTemperature"])
        lo_today = round(min(today_temps)) if today_temps else round(current["screenTemperature"])

        temp_c = round(current["screenTemperature"])
        code = current["significantWeatherCode"]
        wind_kmh = round(current["windSpeed10m"] * 3.6)
        precip = round(current.get("totalPrecipAmount", 0.0), 1)
        condition = MET_CODES.get(code, "Unknown")
        sunrise = sun["sunrise"]
        sunset = sun["sunset"]

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
        draw_icon(draw, 148, 188, 200, code)
        draw.line([(296, 64), (296, 318)], fill=C_BLACK, width=1)

        info_x = 310
        info_x2 = 455

        def info_row(label, value, x, y):
            draw.text((x, y), label, font=font_info_label, fill=grey)
            draw.text((x, y + 22), value, font=font_info_val, fill=C_BLACK)

        row_y = 66
        draw.text((info_x, row_y), condition, font=font_condition, fill=C_BLACK)
        row_y += 42
        info_row("High / Low", f"{hi_today}° / {lo_today}°", info_x, row_y)
        row_y += 58
        info_row("Wind", f"{wind_kmh} km/h", info_x, row_y)
        info_row("Rain", f"{precip} mm", info_x2, row_y)
        row_y += 58
        info_row("Sunrise", sunrise, info_x, row_y)
        info_row("Sunset", sunset, info_x2, row_y)

        # ── Forecast strip ───────────────────────────────────────────
        draw.line([(20, 322), (width - 20, 322)], fill=C_BLACK, width=2)

        future_dates = sorted(d for d in groups if d > today_str)[:3]
        col_w = width // 3

        for i, date_str in enumerate(future_dates):
            summary = _day_summary(date_str, groups[date_str])
            day_name = DAY_NAMES[datetime.strptime(date_str, "%Y-%m-%d").weekday()]
            col_x = i * col_w
            mid = col_x + col_w // 2

            col_centered_text(day_name, font_day, 326, mid)
            draw_icon(draw, col_x + 62, 378, 52, summary["code"])
            draw.text((col_x + 120, 362), f"{round(summary['maxTemp'])}°",
                      font=font_hilo, fill=C_BLACK)

            if i < 2:
                draw.line([(col_x + col_w, 324), (col_x + col_w, height - 8)],
                          fill=C_BLACK, width=1)

        inky.set_image(image)
        inky.show()

    except Exception as e:
        print(f"Weather: render failed: {e}")


if __name__ == "__main__":
    display_weather()
