# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

A Raspberry Pi e-ink display controller for the Pimoroni Inky Impression 4" display (600×448px). It cycles through multiple display modules on a 20-minute rotation, controlled via GPIO buttons.

## Running the Application

```bash
# Activate virtual environment first
source .venv/bin/activate  # Linux/Pi
# .venv\Scripts\activate   # Windows

# Run in background (production)
python3 main.py > /dev/null 2>&1 &

# Run in foreground (development/debugging)
python3 main.py
```

Each display module can also be run standalone:
```bash
python3 apod.py
python3 pihole.py
python3 birthdays.py
python3 date_display.py
python3 stocks.py IGG.L
python3 weather.py
python3 pi_health.py
python3 speedtest_display.py
python3 train_status.py
python3 image.py /path/to/image.png
python3 clear.py
```

`speedtest_runner.py` is not part of the display rotation — it's meant to be run twice daily via cron to collect data that `speedtest_display.py` renders (see below).

There are no automated tests. Manual testing is done by running modules directly. On non-Pi hardware (e.g. Windows dev), set `INKY_PREVIEW=1` so `display.py` writes to `/tmp/inky_preview.png` instead of requiring real GPIO/SPI hardware.

## Architecture

`main.py` is the orchestrator:
- Holds an ordered list of display functions (`display_functions`) and calls one per 20-minute (1200s) cycle, advancing `current_index` and wrapping around.
- `display.py` exposes `get_display()`, an `lru_cache`-wrapped singleton that either returns the real `inky.auto()` handle or, when `INKY_PREVIEW=1`, a `_PreviewDisplay` that saves to `/tmp/inky_preview.png`. All display modules call this instead of `inky.auto()` directly, so the hardware handle is opened exactly once per process (repeated `inky.auto()` calls leak file descriptors).
- A `threading.Lock` (`display_lock`) serializes all writes to the display, since button presses run on gpiozero's callback threads concurrently with the main loop.
- `wake_event` (a `threading.Event`) lets button A interrupt the 1200s sleep to advance immediately.
- Errors inside a display function are caught per-cycle, logged, and the loop advances to the next index rather than crashing.
- Logging goes to `pi-display.log` via a `RotatingFileHandler` (5MB × 3 backups).

Each display module is self-contained and follows the same pattern:
1. Fetch/prepare data (API call, file read, etc.), often with a local JSON cache to avoid hammering rate-limited APIs
2. Draw onto a `PIL.Image` canvas using Roboto fonts from `resources/fonts/`
3. Push to the display via `display.get_display()`
4. Close the image

**Modules and their data sources:**

| Module | Data Source |
|--------|-------------|
| `apod.py` | NASA APOD API (`creds/apod-api.txt`) |
| `pihole.py` | Pi-hole local API (`http://192.168.1.110`, `creds/pihole-api.txt`) |
| `stocks.py` | Yahoo Finance via `yfinance` (cached in `~/.stock_cache.json`, refreshed once/day after 09:00 UTC) |
| `birthdays.py` | `birthdays.json` |
| `date_display.py` | System clock |
| `weather.py` | Met Office Site Specific API (`creds/weather-location.txt` lat/lon, `creds/metoffice-api.txt`) + sunrise-sunset.org; cached in `/tmp/weather_cache.json` (3h TTL) |
| `pi_health.py` | Local system stats via `psutil` and `/sys/class/thermal/thermal_zone0/temp` — no API/creds |
| `speedtest_display.py` | Reads `~/.speedtest_history.json`, written by `speedtest_runner.py` (run via cron, not the main loop) |
| `train_status.py` | Realtime Trains API (`creds/rtt_token.txt`), station codes hardcoded at the top of the file |
| `image.py` | Images from `/home/danny/Pictures` |
| `clear.py` | No data — refreshes display to clear ghosting |
| `google-calendar.py` | Google Calendar OAuth (`creds/client_secret.json`) — **not yet integrated into main loop** |

## Configuration

All configuration is hardcoded directly in the source files — there is no `.env` file:

- **main.py**: image directory, log path, GPIO pin numbers (A=5, B=6, C=16, D=24), cycle interval (1200s), stock symbol, and the ordered `display_functions` list
- **pihole.py**: Pi-hole host URL
- **train_status.py**: station codes and card layout constants (marked `# TODO: tune`)
- Font paths: `./resources/fonts/*.ttf`
- Background images: `./resources/imgs/*.png`

## Credentials

Stored in `creds/` (gitignored). Plain text/JSON files:
- `creds/apod-api.txt` — NASA API key
- `creds/pihole-api.txt` — Pi-hole API password
- `creds/weather-location.txt` — `lat,lon` for the weather module
- `creds/metoffice-api.txt` — Met Office weather API key
- `creds/rtt_token.txt` — Realtime Trains API token
- `creds/client_secret.json` / `token.json` — Google Calendar OAuth (unused module)

## Birthday Data Format

`birthdays.json` uses `"Full Name": "DD-MM-YYYY"` entries.

## Hardware Notes

- Target hardware: Raspberry Pi + Pimoroni Inky Impression 4" (600×448)
- `mock_inky/` provides a no-op mock display for development without hardware (gitignored, not committed) — set `INKY_PREVIEW=1` to use it via `display.py`
- Pillow's deprecated `textsize()`/`getsize()` methods may still be used in some modules — check before relying on them, as they break on Pillow 10+

## Speedtest Setup

`speedtest_display.py` never runs a speedtest itself; it only renders cached results. Data collection is external:
1. `speedtest_runner.py` calls the `speedtest` CLI and appends to `~/.speedtest_history.json` (capped at 60 entries).
2. Schedule it via cron twice daily (midnight and noon) — see README.md for the exact crontab lines.
3. Run it once manually to seed initial data, otherwise the display shows a "no data yet" message.

## Button Controls

- **A** (GPIO 5): Skip to next display
- **B** (GPIO 6): Jump to image display
- **C** (GPIO 16): Unassigned
- **D** (GPIO 24): Trigger display clear/refresh
