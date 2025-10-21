import yfinance as yf
import pandas as pd

def test_ticker(ticker): 
    try:
        print(f"Testing {ticker}...")
        stock = yf.Ticker(ticker)
        hist_data = stock.history(period="1y", interval="1d")

        if hist_data.empty:
            print(f"No historical data for {ticker}")
        else:
            print(f"Fetched {len(hist_data)} rows of data for {ticker}")
            print(hist_data.head())

    except Exception as e:
        print(f"An error occurred while testing {ticker}: {e}")

if __name__ == "__main__":
    print(f"yfinance version: {yf.__version__}")
    
    # Test existing stock
    test_ticker("AAPL")
    
    # Test new indices
    test_ticker("NSE:CNXFINANCE")
    test_ticker("NIFTYMIDSELECT")