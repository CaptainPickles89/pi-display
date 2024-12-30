#  [![My Skills](https://skillicons.dev/icons?i=raspberrypi,python&theme=dark)](https://skillicons.dev) Pi Display 

This Python project was created to have multiple information displays and images cycle through on an e-ink display

## General

This script runs every 15 minutes and will loop through all the functions within the __display_function__ variable in __main.py__, if you do not want to use one of these functions then you will need to remove it from there to stop it being called

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

## Current Features
 - [Pictures](#pictures)
 - [Stocks](#stocks)
 - [PiHole Stats](#pihole-stats)
 - [Birthdays](#birthdays)

## Pictures

This script will take images from the default location of __~/Pictures__, so put any images you want displayed in there and they will be chosen at random to be displayed

## Stocks

This will generate a close price graph of the last 3 months for a given stock (via Yahoo finance), change the stock you wish to see by changing the stock symbol under display_functions in main.py:
```md
lambda: get_stock("IGG.L")
```
Example Output:

![IGG.L Stock Example](/docs/stock_graph.png)

## Pihole Stats

Uses the pihole API to pull back daily stats for ads blocked, DNS queries made and percentage of blocked requests. In order to use this change the __api_url__ within __pihole.py__ to point it to your own instance and ensure you have an api key stored in __/creds/pihole-api.txt__

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
