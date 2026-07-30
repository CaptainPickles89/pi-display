# Pihole Display To-Do

This is a list of features I hope to add if I get chance

## To-Do
 - [ ] Intergrate with Home Assistant
 - [ ] Replace button-polling wait loop in main.py with gpiozero event callbacks (see TODO comment in file) -- currently busy-waits every 100ms
 - [ ] Add a bus/train departure board module (transit API, poll + cache + render, same shape as stocks.py)
 - [ ] Move hardcoded config (image dir, GPIO pins, cycle interval, etc) into a config file instead of scattered across source files

## In Progress
 - [ ] Intergrate with Google API for calendar events

## Done
 - [X] Add readme, todo and requirements files
 - [X] Add a manual clear display
 - [X] Add a manual image display
 - [X] Add error logging to file
 - [X] Refactor the Stocks script
 - [X] Add a general date display
 - [X] Make birthdays.py handle 2 on the same day