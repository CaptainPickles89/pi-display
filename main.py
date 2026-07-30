import os
import random
import logging
import time
import sys
import threading
from functools import partial
from logging.handlers import RotatingFileHandler
from apod import display_apod
from stocks import fetch_and_display_stock
from pihole import show_pihole_stats
from birthdays import check_birthdays
from date_display import get_date
from weather import display_weather
from pi_health import display_pi_health
from speedtest_display import display_speedtest
from image import display_image as show_image
from clear import run_clear
from gpiozero import Button

# Paths
image_dir = "/home/danny/Pictures"  # Change to your image directory
LOG_FILE = "./pi-display.log"  # Error log location

# Log Rotation
max_log_size = 5 * 1024 * 1024  # 5MB
backup_count = 3  # Keep 3 logs
handler = RotatingFileHandler(LOG_FILE, maxBytes=max_log_size, backupCount=backup_count)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger = logging.getLogger("display_logger")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

# Create reusable event
wake_event = threading.Event()

# Lock threads to only allow one to use the display at a time
display_lock = threading.Lock()

# Button setup
button_a = Button(5)
button_b = Button(6)
button_c = Button(16)
button_d = Button(24)

# CLear the screen of any image
def screen_clear():
    if not display_lock.acquire(blocking=False):
        logger.info("Display busy, ignoring button D")
        return
    try:
        run_clear()
        return 0
    except Exception as e:
        logger.error(f"Failed to clear display: {e}", exc_info=True)
        return 1
    finally:
        display_lock.release()

# Show a random picture on the display
def display_image(image_path):
    try:
        print(f"Now loading {image_path} to display")
        show_image(image_path)
    except Exception as e:
        logger.error(f"Failed to display image: {e}", exc_info=True)

# Load images in image dir
image_files = [
            os.path.join(image_dir, f)
            for f in os.listdir(image_dir)
            if f.endswith((".png", ".jpg", ".jpeg"))
        ]

# Skip to the next entry in the loop
def skip_next():
    logger.info("Skipping to next index")
    wake_event.set()

# Skip to showing an image
def skip_to_image():
    if not display_lock.acquire(blocking=False):
        logger.info("Display busy, ignoring button B")
        return
    try:
        logger.info("Skipping to display image")
        display_image(random.choice(image_files))
    finally:
        display_lock.release()
    wake_event.set()

# Main loop
def main():
    logger.info("Starting main loop")
    try:
        display_functions = [
            show_pihole_stats,
            lambda: display_image(random.choice(image_files)),
            partial(fetch_and_display_stock, "IGG.L"),
            display_apod,
            check_birthdays,
            get_date,
            display_weather,
            display_pi_health,
            display_speedtest,
        ]

        current_index = 0
        button_a.when_pressed = skip_next
        button_b.when_pressed = skip_to_image

        while True:
            try:
                print(f"Calling index {current_index}")
                logger.info(f"Display function {display_functions[current_index]}")
                with display_lock:
                    display_functions[current_index]()

                wake_event.wait(1200)
                # reset the event for next loop
                wake_event.clear()

                current_index = (current_index + 1) % len(display_functions)
            except Exception as e:
                logger.error(f"Error during display function: {e}", exc_info=True)
                current_index = (current_index + 1) % len(display_functions)

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(0)

    except Exception as e:
        logger.critical(f"Fatal error in main loop: {e}", exc_info=True)
        sys.exit(1)

    finally:
        logger.info("Process Exiting")

button_d.when_pressed = screen_clear

if __name__ == "__main__":
    main()
