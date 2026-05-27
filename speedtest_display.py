import io
import json
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto

FONT_PATH = "./resources/fonts/Roboto-Medium.ttf"
HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".speedtest_history.json")

STATS_HEIGHT = 158  # px reserved for header + stats before graph


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def display_speedtest():
    history = load_history()

    try:
        inky = auto()
        width, height = inky.resolution

        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        font_header = ImageFont.truetype(FONT_PATH, 32)
        font_sub = ImageFont.truetype(FONT_PATH, 22)
        font_label = ImageFont.truetype(FONT_PATH, 22)
        font_value = ImageFont.truetype(FONT_PATH, 42)

        grey = (100, 100, 100)
        black = (0, 0, 0)

        def col_centred(text, font, y, col_mid, fill=black):
            b = draw.textbbox((0, 0), text, font=font)
            x = col_mid - (b[2] - b[0]) // 2
            draw.text((x, y), text, font=font, fill=fill)

        # ── Header ──────────────────────────────────────────────
        draw.text((20, 14), "Speedtest", font=font_header, fill=black)

        if history:
            last_ts = datetime.fromisoformat(history[-1]["timestamp"])
            last_str = last_ts.strftime("%-d %b %H:%M")
            b = draw.textbbox((0, 0), last_str, font=font_sub)
            draw.text((width - (b[2] - b[0]) - 20, 20), last_str,
                      font=font_sub, fill=grey)

        draw.line([(20, 56), (width - 20, 56)], fill=black, width=2)

        # ── Latest stats ─────────────────────────────────────────
        if not history:
            msg = "No data yet — run speedtest_runner.py"
            b = draw.textbbox((0, 0), msg, font=font_sub)
            draw.text(((width - (b[2] - b[0])) // 2, 100), msg,
                      font=font_sub, fill=grey)
        else:
            latest = history[-1]
            col_w = width // 3
            stats = [
                ("Download", f"{latest['download']}", "Mbps"),
                ("Upload",   f"{latest['upload']}",   "Mbps"),
                ("Ping",     f"{latest['ping']}",      "ms"),
            ]
            for i, (label, value, unit) in enumerate(stats):
                mid = col_w * i + col_w // 2
                col_centred(label, font_label, 64, mid, fill=grey)
                col_centred(value, font_value, 86, mid)
                col_centred(unit, font_label, 132, mid, fill=grey)

            # Column dividers
            for i in (1, 2):
                draw.line([(col_w * i, 62), (col_w * i, STATS_HEIGHT - 4)],
                          fill=(180, 180, 180), width=1)

        draw.line([(20, STATS_HEIGHT), (width - 20, STATS_HEIGHT)],
                  fill=black, width=2)

        # ── Trend graph ──────────────────────────────────────────
        if len(history) >= 2:
            graph_h = height - STATS_HEIGHT
            dpi = 100
            fig, ax = plt.subplots(figsize=(width / dpi, graph_h / dpi), dpi=dpi)
            fig.patch.set_facecolor("white")
            ax.set_facecolor("white")

            timestamps = [datetime.fromisoformat(e["timestamp"]) for e in history]
            downloads  = [e["download"] for e in history]
            uploads    = [e["upload"]   for e in history]

            ax.plot(timestamps, downloads, color="#1a6fc4", linewidth=1.5,
                    label="Download", marker="o", markersize=3)
            ax.plot(timestamps, uploads, color="#e07b00", linewidth=1.5,
                    label="Upload", marker="o", markersize=3)

            ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b"))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.xticks(rotation=30, ha="right", fontsize=8)
            ax.set_ylabel("Mbps", fontsize=9)
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=9, loc="upper left")
            fig.tight_layout(pad=0.4)

            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=dpi)
            plt.close(fig)
            buf.seek(0)

            with Image.open(buf) as graph_img:
                graph_img = graph_img.convert("RGB").resize((width, graph_h))
                image.paste(graph_img, (0, STATS_HEIGHT))

        inky.set_image(image)
        inky.show()

    except Exception as e:
        print(f"Speedtest display: render failed: {e}")


if __name__ == "__main__":
    display_speedtest()
