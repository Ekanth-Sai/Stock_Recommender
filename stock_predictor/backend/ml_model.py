import pandas as pd 
import pandas_ta as ta 

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df.ta.rsi(append = True)
    df.ta.sma(length = 0, append = True)
    df.ta.macd(append = True)
    df.ta.bbands(append = True)
    df.ta.stoch(append = True)

    return df

def get_prediction_with_confidence(data: pd.DataFrame):
    latest_rsi = data["RSI_14"].iloc[-1]
    latest_macd = data["MACD_12_26_9"].iloc[-1] if "MACD_12_26_9" in data.columns else None
    latest_macdh = data["MACDH_12_26_9"].iloc[-1] if "MACDH_12_26_9" in data.columns else None
    latest_macds = data["MACDS_12_26_9"].iloc[-1] if "MACDS_12_26_9" in data.columns else None 

    latest_bb_lower = data["BBL_5_2.0"].iloc[-1] if "BBL_5_2.0" in data.columns else None
    latest_bb_middle = data["BBM_5_2.0"].iloc[-1] if "BBM_5_2.0" in data.columns else None
    latest_bb_upper = data["BBU_5_2.0"].iloc[-1] if "BBU_5_2.0" in data.columns else None
    
    latest_stoch_k = data["STOCHk_14_3_3"].iloc[-1] if "STOCHk_14_3_3" in data.columns else None
    latest_stoch_d = data["STOCHd_14_3_3"].iloc[-1] if "STOCHd_14_3_3" in data.columns else None

    if pd.isna(latest_rsi):
        action = "Hold"
        confidence = 0.50
    elif latest_rsi > 70:
        action = "Sell"
        confidence = min((latest_rsi - 70) / 20, 1.0)  
    elif latest_rsi < 30:
        action = "Hold"
        confidence = 1.0 - (abs(latest_rsi - 50) / 20)
    
    return {
        "action": action,
        "confidence": round(confidence, 2),
        "rsi": round(latest_rsi, 2) if latest_rsi is not None else None,
        "macd": round(latest_macd, 2) if latest_macd is not None else None,
        "macdh": round(latest_macdh, 2) if latest_macdh is not None else None,
        "macds": round(latest_macds, 2) if latest_macds is not None else None,
        "bb_lower": round(latest_bb_lower, 2) if latest_bb_lower is not None else None,
        "bb_middle": round(latest_bb_middle, 2) if latest_bb_middle is not None else None,
        "bb_upper": round(latest_bb_upper, 2) if latest_bb_upper is not None else None,
        "stoch_k": round(latest_stoch_k, 2) if latest_stoch_k is not None else None,
        "stoch_d": round(latest_stoch_d, 2) if latest_stoch_d is not None else None,
    }