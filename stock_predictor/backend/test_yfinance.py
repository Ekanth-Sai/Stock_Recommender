import yfinance as yf 
import pandas as pd 

try:
    print("yfinance test")
    stock = yf.Ticker("AAPL")
    hist_data = stock.history(period = "1y", interval = "1d")

    if hist_data.empty:
        print("No historical data")
    else:
        print(f"Fetched {len(hist_data)} rows of data")
        print(hist_data.head())

except Exception as e:
    print(f"An error occurred: {e}")

print(f"yfinance version: {yf.__version__}")