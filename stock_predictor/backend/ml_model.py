import pandas as pd
import pandas_ta as ta

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators, handling cases with insufficient data"""
    if len(df) < 2:
        return df
    
    # Calculate indicators with error handling
    try:
        df.ta.rsi(append=True)
    except Exception as e:
        print(f"Could not calculate RSI: {e}")
    
    try:
        df.ta.sma(length=20, append=True)
    except Exception as e:
        print(f"Could not calculate SMA: {e}")
    
    try:
        df.ta.macd(append=True)
    except Exception as e:
        print(f"Could not calculate MACD: {e}")
    
    try:
        df.ta.bbands(append=True)
    except Exception as e:
        print(f"Could not calculate Bollinger Bands: {e}")
    
    try:
        df.ta.stoch(append=True)
    except Exception as e:
        print(f"Could not calculate Stochastic: {e}")

    return df

def get_prediction_with_confidence(data: pd.DataFrame):
    """Get prediction with confidence, handling missing indicators gracefully"""
    
    # Safely get indicators with None as default
    latest_rsi = data["RSI_14"].iloc[-1] if "RSI_14" in data.columns and not data["RSI_14"].empty else None
    latest_macd = data["MACD_12_26_9"].iloc[-1] if "MACD_12_26_9" in data.columns and not data["MACD_12_26_9"].empty else None
    latest_macdh = data["MACDh_12_26_9"].iloc[-1] if "MACDh_12_26_9" in data.columns and not data["MACDh_12_26_9"].empty else None
    latest_macds = data["MACDS_12_26_9"].iloc[-1] if "MACDS_12_26_9" in data.columns and not data["MACDS_12_26_9"].empty else None

    latest_bb_lower = data["BBL_5_2.0_2.0"].iloc[-1] if "BBL_5_2.0_2.0" in data.columns and not data["BBL_5_2.0_2.0"].empty else None
    latest_bb_middle = data["BBM_5_2.0_2.0"].iloc[-1] if "BBM_5_2.0_2.0" in data.columns and not data["BBM_5_2.0_2.0"].empty else None
    latest_bb_upper = data["BBU_5_2.0_2.0"].iloc[-1] if "BBU_5_2.0_2.0" in data.columns and not data["BBU_5_2.0_2.0"].empty else None

    latest_stoch_k = data["STOCHk_14_3_3"].iloc[-1] if "STOCHk_14_3_3" in data.columns and not data["STOCHk_14_3_3"].empty else None
    latest_stoch_d = data["STOCHd_14_3_3"].iloc[-1] if "STOCHd_14_3_3" in data.columns and not data["STOCHd_14_3_3"].empty else None

    # Check if RSI is valid
    if latest_rsi is None or pd.isna(latest_rsi):
        action = "Hold"
        confidence = 0.50
    elif latest_rsi > 70:
        action = "Sell"
        confidence = min((latest_rsi - 70) / 30, 1.0)  
    elif latest_rsi < 30:
        action = "Buy"
        confidence = min((30 - latest_rsi) / 30, 1.0)  
    else:  
        action = "Hold"
        confidence = 1.0 - abs(latest_rsi - 50) / 20.0

    return {
        "action": action,
        "confidence": round(confidence, 2),
        "rsi": round(latest_rsi, 2) if latest_rsi is not None and not pd.isna(latest_rsi) else None,
        "macd": round(latest_macd, 2) if latest_macd is not None and not pd.isna(latest_macd) else None,
        "macdh": round(latest_macdh, 2) if latest_macdh is not None and not pd.isna(latest_macdh) else None,
        "macds": round(latest_macds, 2) if latest_macds is not None and not pd.isna(latest_macds) else None,
        "bb_lower": round(latest_bb_lower, 2) if latest_bb_lower is not None and not pd.isna(latest_bb_lower) else None,
        "bb_middle": round(latest_bb_middle, 2) if latest_bb_middle is not None and not pd.isna(latest_bb_middle) else None,
        "bb_upper": round(latest_bb_upper, 2) if latest_bb_upper is not None and not pd.isna(latest_bb_upper) else None,
        "stoch_k": round(latest_stoch_k, 2) if latest_stoch_k is not None and not pd.isna(latest_stoch_k) else None,
        "stoch_d": round(latest_stoch_d, 2) if latest_stoch_d is not None and not pd.isna(latest_stoch_d) else None,
    }