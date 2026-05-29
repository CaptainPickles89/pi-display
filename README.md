#  Pi Display 
![Skills](https://skills-icons.vercel.app/api/icons?i=raspberrypi,python)

This Python project was created to have multiple information displays and images cycle through on an e-ink display

## General

This script runs every 20 minutes and will loop through all the functions within the __display_function__ variable in __main.py__, if you do not want to use one of these functions then you will need to remove it from there to stop it being called. If you have an e-ink with buttons pressing __Button A__ skips to the next display function

Each function should be modular so you can use them all running main.py or you can call just specific functions that you want to use, such as:
```md
python3 pihole.py
```
## Parts
 - Raspberry Pi (any model should do as long as it has a GPIO header)
 - e-ink display (I'm using the [4" Inky Impressions](https://shop.pimoroni.com/products/inky-impression-4?variant=39599238807635) display)
 - Internet connection for the Raspberry Pi

## Installation
- Follow the guide for which display you have to install it onto your Raspberry Pi
- Clone this repo to your device:
```bash
git clone https://github.com/CaptainPickles89/pi-display.git
```
- If you do not have one, create a python3 virtual environment and install the project's requirements
```bash
$ python3 -m venv eink_display_venv
$ source eink_display_venv/bin/activate
(eink_display_venv) $ pip install -r requirements.txt
```
- Add API keys, currently api keys are needed for the PiHole stats, once you have your key save it in __/creds__ in a file called __pihole-api.txt__
- Now all you have to do is run it in the background, the following will run it silently in the background with no output to terminal:
```bash
python3 main.py > /dev/null 2>&1 & 
```

Any error logging is currently sent to __pi-display.log__ in the project directory should you face any issues

## Current Features
 - [Pictures](#pictures)
 - [Stocks](#stocks)
 - [PiHole Stats](#pihole-stats)
 - [Birthdays](#birthdays)
 - [NASA APOD](#nasa-apod)
 - [Clear](#clear)
 - [Date](#date)
 - [Weather](#weather)
 - [Pi Health](#pi-health)
 - [Speedtest](#speedtest)

## Pictures

This script will take images from the location of __image_dir__ set within the __main.py__ script, so put any images you want displayed in there and they will be chosen at random to be displayed. If you have a e-ink with buttons, pressing __Button B__ will force this to run immediatly regardless fo where the current rotation is

## Stocks

This will generate a close price graph of the last 6 months for a given stock (via Yahoo finance), change the stock you wish to see by changing the stock symbol under display_functions in main.py:
```python
partial(fetch_and_display_stock, "IGG.L")
```

Stock data is cached and refreshed once per day. The cache is considered stale after 09:00 UTC, regardless of your local timezone.
Example Output:

![IGG.L Stock Example](/docs/stock_example.png)

## Pihole Stats

Uses the pihole API to pull back daily stats for ads blocked, DNS queries made and percentage of blocked requests. In order to use this change the __api_url__ within __pihole.py__ to point it to your own instance and ensure you have an api key stored in __/creds/pihole-api.txt__

Example Output:
![Pihole Stats](/docs/pihole_example.png)

## Birthdays

Add in a JSON of birthdays you want to keep track of and your display will let you know! create a file in the project called __birthdays.json__ and lay them out in the following format:
```json
{
    "Person 1": "01-11-1990",
    "Person 2": "01-03-1990",
    "Person 3": "01-02-1990"
}
```
If today is someones birthday, then the display should let you know.

## NASA APOD

NASA APOD or Astronomy Picture Of the Day, will call the NASA API and show whatever the picture of the day is with its title. You will need to signup for a free [NASA API here](https://api.nasa.gov/), and then add it into the __/creds__ folder as __apod-api.txt__.

Example Output:

![APOD Example](/docs/apod_example.png)

## Clear
If you have an e-ink with buttons pressing __Button D__ triggers the clear function which cycles blocks of avialble colours multiple times in order to clear any potential image ghosting

## Date
This function pulls todays date and displays the day, date and month

Example Output:

![Date Example](/docs/date_example.png)

## Weather

Fetches current conditions and a 3-day forecast from [Open-Meteo](https://open-meteo.com/) (free, no API key required). Displays current temperature, weather condition, wind speed, and daily high/low with rain probability for the next 3 days.

To configure your location, create a file at __creds/weather-location.txt__ containing your latitude and longitude separated by a comma:
```
51.5074,-0.1278
```

## Pi Health

Displays a live snapshot of the Raspberry Pi's system stats: CPU temperature, CPU usage %, RAM usage, and disk usage. No external API or credentials required.

## Speedtest

Shows the latest download speed, upload speed, and ping, along with a trend graph of historical results. Results are collected twice daily (midnight and noon) by a separate runner script, so the display always shows cached data without blocking the main loop.

### Setup

**1. Install the dependency:**
```bash
pip install speedtest-cli
```

**2. Add cron jobs to run the speedtest at midnight and noon** (`crontab -e`):
```
0 0  * * * /usr/bin/python3 /home/danny/pi-display/speedtest_runner.py
0 12 * * * /usr/bin/python3 /home/danny/pi-display/speedtest_runner.py
```
Adjust the path to match your install location. If using a virtual environment, replace `/usr/bin/python3` with the path to your venv Python binary (e.g. `/home/danny/pi-display/eink_display_venv/bin/python3`).

**3. Seed your first result** so the display has data straight away:
```bash
python3 speedtest_runner.py
```

Results are stored in __~/.speedtest_history.json__ (up to 60 entries, ~30 days). The display will show a "no data yet" message until the first run completes.

## Credits

This project uses the **Roboto** font, which is licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).  
Roboto is a trademark of Google, and the font is made available by [Google Fonts](https://fonts.google.com/).

This project also uses the following libraries and resources:

- [Inky Impression](https://github.com/pimoroni/inky) by Pimoroni
- [yfinance](https://pypi.org/project/yfinance/)
- [Pillow](https://pillow.readthedocs.io/)
- And many others...

Special thanks to [ChatGPT](https://chatgpt.com) by OpenAI and [Claude Code](https://claude.ai/code) by Anthropic for assistance with coding and design ideas.

Please refer to the `LICENSE` file for more detailed license information.
