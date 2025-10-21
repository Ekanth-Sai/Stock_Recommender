import yfinance as yf 
import pandas as pd 
from fastapi import HTTPException 

from ml_model import get_prediction_with_confidence, calculate_technical_indicators

def convert_nan_to_none(obj):
    if isinstance(obj, dict):
        return {k : convert_nan_to_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_nan_to_none(elem) for elem in obj] 
    elif pd.isna(obj):
        return None 
    return obj 

def get_stock_prediction_data(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        hist_data = stock.history(period="1d", interval="1m")

        if hist_data.empty:
            raise HTTPException(
                status_code =400,
                detail = "Ticker not found or data unavailable" 
            )
        
        hist_data_with_indicators = calculate_technical_indicators(hist_data.copy()) 

        chart_data = stock.history(period = "1d", interval = "1m")
        prediction_result = get_prediction_with_confidence(hist_data_with_indicators) 

        hi = hist_data_with_indicators 
        historical_indicators = {
            "labels": hi.index.strftime("%H:%M").tolist(),
            "close": hi["Close"].tolist(),
            "rsi": hi["RSI_14"].tolist(),
            "macd": hi["MACD_12_26_9"].tolist(),
            "macdh": hist_data_with_indicators["MACDh_12_26_9"].tolist(),
            "macds": hi["MACDs_12_26_9"].tolist(),
            "bb_upper": hi["BBU_5_2.0_2.0"].tolist(),
            "bb_lower": hi["BBL_5_2.0_2.0"].tolist(),
            "bb_middle": hi["BBM_5_2.0_2.0"].tolist(),
            "stoch_k": hi["STOCHk_14_3_3"].tolist(),
            "stoch_d": hi["STOCHd_14_3_3"].tolist(),
        }

        historical_indicators = convert_nan_to_none(historical_indicators)
        prediction_result = convert_nan_to_none(prediction_result)
        chart_data = convert_nan_to_none(chart_data)

        return {
            "chartData": {
                "labels": chart_data.index.strftime("%H:%M").tolist(),
                "values": chart_data["Close"].tolist(),
            },
            "historicalIndicators": historical_indicators,
            "prediction": prediction_result,
            "indicators": {},
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unhandled error in get_stock_prediction_data: {e}")
        raise HTTPException(status_code = 500, detail = "Internal server error")

def get_index_pre_analysis_data(ticker: str):
    try:
        index_data = yf.Ticker(ticker)
        hist_data = index_data.history(period="1d", interval="1m")

        if hist_data.empty:
            raise HTTPException(
                status_code =400,
                detail = "Index Ticker not found or data unavailable" 
            )
        
        hist_data_with_indicators = calculate_technical_indicators(hist_data.copy()) 

        chart_data = index_data.history(period = "1d", interval = "1m")
        prediction_result = get_prediction_with_confidence(hist_data_with_indicators) 

        hi = hist_data_with_indicators 
        historical_indicators = {
            "labels": hi.index.strftime("%H:%M").tolist(),
            "close": hi["Close"].tolist(),
            "rsi": hi["RSI_14"].tolist(),
            "macd": hi["MACD_12_26_9"].tolist(),
            "macdh": hist_data_with_indicators["MACDh_12_26_9"].tolist(),
            "macds": hi["MACDs_12_26_9"].tolist(),
            "bb_upper": hi["BBU_5_2.0_2.0"].tolist(),
            "bb_lower": hi["BBL_5_2.0_2.0"].tolist(),
            "bb_middle": hi["BBM_5_2.0_2.0"].tolist(),
            "stoch_k": hi["STOCHk_14_3_3"].tolist(),
            "stoch_d": hi["STOCHd_14_3_3"].tolist(),
        }

        historical_indicators = convert_nan_to_none(historical_indicators)
        prediction_result = convert_nan_to_none(prediction_result)
        chart_data = convert_nan_to_none(chart_data)

        return {
            "chartData": {
                "labels": chart_data.index.strftime("%H:%M").tolist(),
                "values": chart_data["Close"].tolist(),
            },
            "historicalIndicators": historical_indicators,
            "prediction": prediction_result,
            "indicators": {},
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unhandled error in get_index_pre_analysis_data: {e}")
        raise HTTPException(status_code = 500, detail = "Internal server error")