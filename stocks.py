import sys
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto


def fetch_and_display_stock(symbol):
    # Fetch stock data
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="6mo")  # Get data for the last 3 months

        if hist.empty:
            print(f"No data found for {symbol}")
            return

        # Extract latest close price
        latest_close = hist["Close"].iloc[-1]
        previous_close = hist["Close"].iloc[-2]
        price_change = latest_close - previous_close
        direction = "▲" if price_change > 0 else "▼"

        # Display current stock price and direction
        print(
            f"The latest closing price for {symbol} is {latest_close:.2f} ({direction}{abs(price_change):.2f})"
        )

        # Plot a graph of the stock's performance
        plt.figure(figsize=(4, 3))  # Adjust size to fit the Inky display
        plt.plot(hist.index, hist["Close"], label="Closing Price", color="blue")
        # Format the x-axis to show 'XX-MMM' style labels
        ax = plt.gca()  # Get the current axis
        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%d-%b")
        )  # Format as '10-Dec'
        # Optional: Rotate the x-axis labels if they're cramped
        plt.xticks(rotation=45)
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.title(f"{symbol} - 6 Month Performance")
        plt.grid(True)
        plt.legend()

        # Save the plot as an image
        graph_path = "/tmp/stock_graph.png"  # Save the image in /tmp
        plt.savefig(graph_path, bbox_inches="tight")
        plt.close()

        # Display the graph on the Inky
        print(graph_path)
        display_stock_graph(graph_path)
    except Exception as e:
        print(f"Error in stock script: {e}")
        sys.exit(1)


def display_stock_graph(graph_path):
    # Prepare the display
    inky = auto()
    saturation = 0.5
    with Image.open(graph_path) as img:
        resizedimage = img.resize(inky.resolution)
        try:
            inky.set_image(resizedimage, saturation=saturation)
        except TypeError:
            inky.set_image(resizedimage)
        inky.show()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Stock symbol not provided")
        sys.exit(1)
    symbol = sys.argv[1]
    print(f"Running stock script for {symbol}")
    fetch_and_display_stock(symbol)
