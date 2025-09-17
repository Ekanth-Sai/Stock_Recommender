import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_historical_data(ticker: str, period: str = "1y", interval = "1d"): 
    tk = yf.Ticker(ticker)
    df = tk.history(period = period, interval = interval, auto_adjust = False)
    df = df.rename(columns = {c : c.lower() for c in df.columns})
    
    return df

def fetch_latest_price(ticker: str):
    tk = yf.Ticker(ticker)
    data = tk.history(period="2d", interval="1m", auto_adjust=False)
    
    if data.empty:
        return None
    last = data.iloc[-1]

    return {
        'timestamp': last.name.to_pydatetime(),
        'Open': last['Open'],
        'High': last['High'],
        'Low': last['Low'],
        'Close': last['Close'],
        'Volume': last['Volume']
    }