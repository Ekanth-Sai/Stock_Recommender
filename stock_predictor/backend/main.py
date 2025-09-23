from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf 
import pandas as pd 
import numpy as np 
from ml_model import get_prediction_with_confidence, calculate_technical_indicators 

app = FastAPI() 

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)



@app.get("/api/stock/{ticker}")
async def get_stock_data(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        hist_data = stock.history(period = "1y", interval = "1d")

        if hist_data.empty:
            raise HTTPException(status_code = 400, detail = "Ticker not found or data unavailable")
        
        hist_data_with_indicators = calculate_technical_indicators(hist_data.copy())

        chart_data = stock.history(period = "1d", interval = "1m")

        prediction_result = get_prediction_with_confidence(hist_data_with_indicators)

        historical_indicators = {
            "labels": hist_data_with_indicators.index.strftime("%Y-%m-%d").tolist(),
            "close": hist_data_with_indicators["Close"].tolist(),
            "rsi": hist_data_with_indicators["RSI_14"].tolist(),
            "macd": hist_data_with_indicators["MACD_12_26_9"].tolist(),
            "macdh": hist_data_with_indicators["MACDH_12_26_9"].tolist(),
            "bb_upper": hist_data_with_indicators["BBU_5_2.0"].tolist(),
            "bb_middle": hist_data_with_indicators["BBM_5_2.0"].tolist(),
            "bb_lower": hist_data_with_indicators["BBL_5_2.0"].tolist(),
            "stoch_k": hist_data_with_indicators["STOCHk_14_3_3"].tolist(),
            "stoch_d": hist_data_with_indicators["STOCHd_14_3_3"].tolist()
        }

        return {
            "chartData": {
                "labels": chart_data.index.strftime("%H : %M").tolist(),
                "values": chart_data["Close"].tolist()
            },
            "historicalIndicators": historical_indicators,
            "prediction": prediction_result,
            "indicators": {}
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

        """prediction_result = {
            "action": "Hold",
            "confidence": 0.5,
            "rsi": None, "macd": None, "macdh": None, "macds": None,
            "bb_lower": None, "bb_middle": None, "bb_upper": None,
            "stoch_k": None, "stoch_d": None
        }

        historical_indicators = {
            "labels": hist_data_with_indicators.index.strftime("%Y-%m-%d").tolist(),
            "close": hist_data_with_indicators["Close"].tolist(),
            "rsi": hist_data_with_indicators["RSI_14"].tolist(),
            "macd": hist_data_with_indicators["MACD_12_26_9"].tolist(),
            "macdh": hist_data_with_indicators["MACDH_12_26_9"].tolist(),
            "macds": hist_data_with_indicators["MACDS_12_26_9"].tolist(),
            "bb_upper": hist_data_with_indicators["BBU_5_2.0"].tolist(),
            "bb_middle": hist_data_with_indicators["BBM_5_2.0"].tolist(),
            "bb_lower": hist_data_with_indicators["BBL_5_2.0"].tolist(),
            "stoch_k": hist_data_with_indicators["STOCHk_14_3_3"].tolist(),
            "stoch_d": hist_data_with_indicators["STOCHd_14_3_3"].tolist(),
        }"""

        return {
            "chartData": {
                "labels": chart_data.index.strftime("%H : %M").tolist(),
                "values": chart_data["Close"].tolist(),
            },
            # "historicalIndicators": historical_indicators,
            # "prediction" : prediction_result,
            "indicators": {}
        }
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))