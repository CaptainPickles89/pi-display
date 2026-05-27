import psutil
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto
from datetime import datetime

FONT_PATH = "./resources/fonts/Roboto-Medium.ttf"
TEMP_FILE = "/sys/class/thermal/thermal_zone0/temp"


def get_cpu_temp():
    try:
        with open(TEMP_FILE) as f:
            return round(int(f.read().strip()) / 1000, 1)
    except Exception:
        return None


def fmt_bytes(b):
    return round(b / (1024 ** 3), 1)


def display_pi_health():
    try:
        inky = auto()
        width, height = inky.resolution

        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        font_header = ImageFont.truetype(FONT_PATH, 32)
        font_label = ImageFont.truetype(FONT_PATH, 28)
        font_value = ImageFont.truetype(FONT_PATH, 58)
        font_sub = ImageFont.truetype(FONT_PATH, 24)

        # Header
        draw.text((20, 16), "Pi Health", font=font_header, fill="black")
        now_str = datetime.now().strftime("%d %b %H:%M")
        bbox = draw.textbbox((0, 0), now_str, font=font_label)
        draw.text((width - (bbox[2] - bbox[0]) - 20, 18), now_str, font=font_label, fill="black")

        draw.line([(20, 62), (width - 20, 62)], fill="black", width=2)

        # Gather stats
        cpu_temp = get_cpu_temp()
        cpu_pct = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        temp_str = f"{cpu_temp}°C" if cpu_temp is not None else "N/A"
        cpu_str = f"{cpu_pct}%"
        ram_str = f"{ram.percent}%"
        ram_sub = f"{fmt_bytes(ram.used)} / {fmt_bytes(ram.total)} GB"
        disk_str = f"{disk.percent}%"
        disk_sub = f"{fmt_bytes(disk.used)} / {fmt_bytes(disk.total)} GB"

        # Layout: 2x2 grid
        # col_x: left=50, right=330  row_y: top=90, bottom=270
        cells = [
            ("CPU Temp", temp_str, None, 50, 90),
            ("CPU Usage", cpu_str, None, 330, 90),
            ("RAM", ram_str, ram_sub, 50, 270),
            ("Disk", disk_str, disk_sub, 330, 270),
        ]

        for label, value, sub, x, y in cells:
            draw.text((x, y), label, font=font_label, fill="black")
            draw.text((x, y + 34), value, font=font_value, fill="black")
            if sub:
                draw.text((x, y + 100), sub, font=font_sub, fill="black")

        # Grid lines
        draw.line([(width // 2, 70), (width // 2, height - 10)], fill="black", width=1)
        draw.line([(20, height // 2 + 20), (width - 20, height // 2 + 20)], fill="black", width=1)

        inky.set_image(image)
        inky.show()

    except Exception as e:
        print(f"Pi health: render failed: {e}")


if __name__ == "__main__":
    display_pi_health()
