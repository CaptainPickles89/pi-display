import os
import random
import logging
import time
import sys
import traceback
import subprocess
from logging.handlers import RotatingFileHandler
from apod import display_apod
from pihole import show_pihole_stats
from birthdays import read_birthdays
from gpiozero import Button
from inky.auto import auto

# Initialize the Inky Impression
inky_display = auto()
inky_display.set_border(inky_display.WHITE)

# Button setup
button_a = Button(5)  
button_b = Button(6)
button_c = Button(16)
button_d = Button(24)

# Paths
image_dir = "/home/danny/Pictures"  # Change to your image directory
LOG_FILE = "./pi-display.log"       # Error log location
birthday_file = "./birthdays.json"  # Birthday json location

# Log Rotation
max_log_size = 5 * 1024 * 1024 # 5MB
backup_count = 3 # Keep 3 logs
handler = RotatingFileHandler(LOG_FILE, maxBytes=max_log_size, backupCount=backup_count)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger = logging.getLogger("display_logger")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

def log_error(message):
    try:
        # Logs error messages to specified file
        with open(LOG_FILE, "a") as log_file:
            log_file.write(f"{time.strftime('%d-%m-%Y %H:%M:%S')} - {message}\n")
            log_file.flush()
    except Exception as e:
        print(f"Failed to log error {e}")

def get_stock(symbol):
    try:
        subprocess.run(['python3', 'stocks.py', symbol])
        image_path="/tmp/stock_graph.png"
        print(f"Displaying stock graph from {image_path}")
        display_image(image_path)
        return 0  # success
    except Exception as e:
        print(f"Failed to get stock data for {symbol}: {e}")
        log_error(f"Failed to get stock {symbol}: {e}")
        return 1  # failure

# Clear the e-ink screen 
def screen_clear():
    try:
        subprocess.run(["python3", "clear.py"])
        return 0  # success
    except Exception as e:
        print(f"Failed to clear display: {e}")
        log_error(f"Failed to clear display: {e}")
        return 1  # failure

# Display an image
def display_image(image_path):
    try:
        print(f"Now loading {image_path} to display")
        subprocess.run(['python3', 'image.py', image_path])
    except Exception as e:
        print(f"Failed to display image: {e}")
        log_error(f"Failed to display image: {e}")


# Main loop
def main():
    logger.info(f"Starting main loop")
    try:
        image_files = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        display_functions = [
            lambda: show_pihole_stats(),
            lambda: display_image(random.choice(image_files)),
            lambda: get_stock("IGG.L"),
            lambda: display_apod(),
            lambda: read_birthdays(birthday_file),
            ]
        
        current_index = 0

        while True:
            try:
                print(f"Calling index {current_index}")
                print(f"Display function {display_functions[current_index]}")
                if display_functions[current_index]:
                    display_functions[current_index]()
                else:
                    print(f"Error: Function at index {current_index} is None")
                    log_error(f"Error: Function at index {current_index} is None")
                
                # Wait for 15 minutes or button press
                start_time = time.time()
                while time.time() - start_time < 900:  # 15 minutes
                    if button_a.is_pressed:
                        print("Skipping to next function")
                        break    
                    elif button_b.is_pressed:
                        current_index = 0
                        print("Jumping to displaying a picture")
                        break
                    elif button_d.is_pressed:
                        print("Forcing a screen clean")
                        screen_clear()
                        break
                    time.sleep(0.1)  # Check button press every 100ms
                
                current_index = (current_index + 1) % len(display_functions)
            except Exception as e:
                log_error(f"Error during display function: {e}")
                log_error(traceback.format_exc())               
                current_index = (current_index + 1) % len(display_functions)

    except Exception as e:
        # Log the final error and re-raise it to stop the script
        logger.error(f"Fatal error in main loop: {e}", exc_info=True)
        log_error(traceback.format_exc())
        sys.exit(1)
        raise

    except KeyboardInterrupt:
        logger.info("Process intterupted by user")
        sys.exit(0)

    finally:
        logger.info("Process Exiting")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(f"Unhandled exception: {e}")
        log_error(traceback.format_exc())
        logger.critical(f"Fatal Error: {e}", exc_info=True)
