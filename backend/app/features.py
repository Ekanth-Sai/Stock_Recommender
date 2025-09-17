import numpy as np 
import pandas as pd 

def sma(series: pd.Series, window: int):
    return series.rolling(window).mean()

def ema(series: pd.Series, span: int):
    return series.ewm(span=span, adjust=False).mean()

def rsi(series: pd.Series, window: int):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def macd(series: pd.Series, fast = 12, slow_span = 26, signal_span = 9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow_span)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_span, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def atr(df: pd.DataFrame, window: 14):
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window).mean()

def bollinger_bands(series, window = 20):
    sma = series.rolling(window).mean()
    std = series.rolling(window).std()
    upper = sma * 2 * std
    lower = sma - 2 * std
    return upper, lower

def add_techincal_indicators(df: pd.DataFrame):
    df = df.copy()
    df['sma_20'] = sma(df['close'], 20)
    df['sma_50'] = sma(df['close'], 50)
    df['ema_20'] = ema(df['close'], 20)
    df['ema_50'] = ema(df['close'], 50)
    df['rsi_14'] = rsi(df['close'], 14)
    macd_line, signal_line, histogram = macd(df['close'])
    df['macd'] = macd_line
    df['macd_signal'] = signal_line
    df['macd_histogram'] = histogram
    df['atr_14'] = atr(df, 14)
    df['Return_1d'] = df['close'].pct_change(1)
    upper, lower = bollinger_bands(df['close'])
    df['bb_upper'] = upper
    df['bb_lower'] = lower
    
    return df


