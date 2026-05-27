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

        # Grid lines first (drawn behind text)
        mid_x = width // 2
        mid_y = 62 + (height - 62) // 2  # vertical midpoint of content area
        draw.line([(mid_x, 70), (mid_x, height - 10)], fill="black", width=1)
        draw.line([(20, mid_y), (width - 20, mid_y)], fill="black", width=1)

        # 2x2 grid — centre content in each quadrant
        col_w = width // 2
        row_h = (height - 62) // 2

        def draw_cell(label, value, sub, col, row):
            # Quadrant bounds
            qx = col * col_w
            qy = 62 + row * row_h

            # Measure total content block height
            lh = draw.textbbox((0, 0), label, font=font_label)
            vh = draw.textbbox((0, 0), value, font=font_value)
            label_h = lh[3] - lh[1]
            value_h = vh[3] - vh[1]
            gap = 6
            sub_gap = 18
            block_h = label_h + gap + value_h
            if sub:
                sh = draw.textbbox((0, 0), sub, font=font_sub)
                block_h += sub_gap + (sh[3] - sh[1])

            # Vertical start to centre block in quadrant
            ty = qy + (row_h - block_h) // 2

            def draw_centred(text, font, y):
                b = draw.textbbox((0, 0), text, font=font)
                tx = qx + (col_w - (b[2] - b[0])) // 2
                draw.text((tx, y), text, font=font, fill="black")

            draw_centred(label, font_label, ty)
            ty += label_h + gap
            draw_centred(value, font_value, ty)
            if sub:
                ty += value_h + sub_gap
                draw_centred(sub, font_sub, ty)

        draw_cell("CPU Temp",  temp_str, None,    col=0, row=0)
        draw_cell("CPU Usage", cpu_str,  None,    col=1, row=0)
        draw_cell("RAM",       ram_str,  ram_sub, col=0, row=1)
        draw_cell("Disk",      disk_str, disk_sub, col=1, row=1)

        inky.set_image(image)
        inky.show()

    except Exception as e:
        print(f"Pi health: render failed: {e}")


if __name__ == "__main__":
    display_pi_health()
