import sys
import yfinance as yf
import matplotlib.pyplot as plt

def fetch_and_display_stock(symbol):
    # Fetch stock data
    stock = yf.Ticker(symbol)
    hist = stock.history(period="3m")  # Get data for the last 3 months
    
    if hist.empty:
        print(f"No data found for {symbol}")
        return
    
    # Extract latest close price
    latest_close = hist["Close"].iloc[-1]
    previous_close = hist["Close"].iloc[-2]
    price_change = latest_close - previous_close
    direction = "▲" if price_change > 0 else "▼"
    
    # Display current stock price and direction
    print(f"The latest closing price for {symbol} is {latest_close:.2f} ({direction}{abs(price_change):.2f})")

    # Plot a graph of the stock's performance
    plt.figure(figsize=(4, 3))  # Adjust size to fit the Inky display
    plt.plot(hist.index, hist["Close"], marker="o", label="Closing Price", color="blue")
    plt.xlabel("Date (M)")
    plt.ylabel("Price")
    plt.title(f"{symbol} - 3 Month Performance")
    plt.grid(True)
    plt.legend()

    # Save the plot as an image
    graph_path = "/tmp/stock_graph.png"  # Temporary path for the graph
    plt.savefig(graph_path, bbox_inches="tight")
    plt.close()

    # Display the graph on the Inky
    print(graph_path)
    return graph_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        symbol = sys.argv[1]  # Get the symbol from the command-line argument
    else:
        print("No image path provided!")
