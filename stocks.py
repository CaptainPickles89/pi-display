import os
import sys
import json
import time
from datetime import datetime, timezone
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PIL import Image
from inky.auto import auto

CACHE_FILE = "/tmp/stock_cache.json"

# ----------------- Cache Utilities -----------------
def load_cache():
    """Load the JSON cache from disk."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    """Save the JSON cache to disk."""
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


def is_new_market_day(last_fetch_ts):
    """Return True if the last fetch was before today 09:00 UK time."""
    now_utc = datetime.now(timezone.utc)
    today_9am_utc = datetime(year=now_utc.year, month=now_utc.month,
                             day=now_utc.day, hour=9, tzinfo=timezone.utc)
    return last_fetch_ts < today_9am_utc.timestamp()


# ----------------- Stock Fetching -----------------
def fetch_stock(symbol):
    """
    Fetch stock price from Yahoo or from cache if available.
    Returns the latest close price and price change from previous day.
    """
    cache = load_cache()
    cached_entry = cache.get(symbol)
    use_cache = False

    if cached_entry:
        last_fetch_ts = cached_entry["timestamp"]
        if not is_new_market_day(last_fetch_ts):
            use_cache = True

    if use_cache:
        latest_close = cached_entry["latest_close"]
        previous_close = cached_entry["previous_close"]
        print(f"Using cached price for {symbol}: {latest_close:.2f}")
    else:
        stock = yf.Ticker(symbol)
        for attempt in range(3):
            try:
                hist = stock.history(period="6mo")
                if not hist.empty:
                    latest_close = hist["Close"].iloc[-1]
                    previous_close = hist["Close"].iloc[-2]
                    cache[symbol] = {
                        "latest_close": latest_close,
                        "previous_close": previous_close,
                        "timestamp": time.time()
                    }
                    save_cache(cache)
                    break
            except Exception as e:
                print(f"Attempt {attempt+1} failed for {symbol}: {e}")
            print(f"Yahoo rate-limited request, retrying {attempt+1}/3...")
            time.sleep(5)
        else:
            if cached_entry:
                latest_close = cached_entry["latest_close"]
                previous_close = cached_entry["previous_close"]
                print(f"Using stale cached price for {symbol}: {latest_close:.2f}")
            else:
                print(f"No data available for {symbol}")
                return None, None

    price_change = latest_close - previous_close
    return latest_close, price_change


# ----------------- Display Utilities -----------------
def display_stock_graph(graph_path):
    """Display the stock graph on the Inky display."""
    inky = auto()
    saturation = 0.5
    with Image.open(graph_path) as img:
        resizedimage = img.resize(inky.resolution)
        try:
            inky.set_image(resizedimage, saturation=saturation)
        except TypeError:
            inky.set_image(resizedimage)
        inky.show()


# ----------------- Main Function -----------------
def fetch_and_display_stock(symbol):
    """Fetch stock, print latest price, plot graph, and display on Inky."""
    latest_close, price_change = fetch_stock(symbol)
    if latest_close is None:
        print(f"No price data for {symbol}")
        return

    direction = "▲" if price_change > 0 else "▼"
    print(f"The latest closing price for {symbol} is {latest_close:.2f} ({direction}{abs(price_change):.2f})")

    # Fetch historical data for plotting (6 months)
    stock = yf.Ticker(symbol)
    hist = stock.history(period="6mo")
    if hist.empty:
        print(f"No historical data for {symbol}")
        return

    # Plot graph
    plt.figure(figsize=(4, 3))
    plt.plot(hist.index, hist["Close"], label="Closing Price", color="blue")
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    plt.xticks(rotation=45)
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title(f"{symbol} - 6 Month Performance")
    plt.grid(True)
    plt.legend()

    # Save and display
    graph_path = "/tmp/stock_graph.png"
    plt.savefig(graph_path, bbox_inches="tight")
    plt.close()
    display_stock_graph(graph_path)


# ----------------- CLI Entry Point -----------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Stock symbol not provided")
        sys.exit(1)
    symbol = sys.argv[1]
    print(f"Running stock script for {symbol}")
    fetch_and_display_stock(symbol)
