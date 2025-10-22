import yfinance as yf 
import pandas as pd 
from fastapi import HTTPException 

from ml_model import get_prediction_with_confidence, calculate_technical_indicators

def convert_nan_to_none(obj):
    if isinstance(obj, dict):
        return {k: convert_nan_to_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_nan_to_none(elem) for elem in obj] 
    elif isinstance(obj, (pd.DataFrame, pd.Series)):
        return convert_nan_to_none(obj.to_dict() if isinstance(obj, pd.Series) else obj.to_dict('list'))
    elif pd.isna(obj):
        return None 
    return obj 

def get_stock_prediction_data(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        hist_data = stock.history(period="1d", interval="1m")
        if hist_data.empty:
            print(f"No intraday data for {ticker}, trying daily data...")
            hist_data = stock.history(period="30d", interval="1d")
            interval_type = "daily"
        else:
            interval_type = "intraday"

        if hist_data.empty:
            if ticker in ['^NSEI', '^BSESN', '^NSEBANK', 'NIFTY_FIN_SERVICE.NS', 'NIFTY_MID_SELECT.NS']:
                print(f"Trying alternative fetch for {ticker}...")
                hist_data = stock.history(period="3mo", interval="1d")
            
            if hist_data.empty:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ticker {ticker} not found or data unavailable. For Indian indices, market may be closed or try again later." 
                )
        
        hist_data_with_indicators = calculate_technical_indicators(hist_data.copy()) 
        chart_data = hist_data.copy()
        prediction_result = get_prediction_with_confidence(hist_data_with_indicators) 

        hi = hist_data_with_indicators 
        
        if interval_type == "intraday":
            labels = hi.index.strftime("%H:%M").tolist()
            chart_labels = chart_data.index.strftime("%H:%M").tolist()
        else:
            labels = hi.index.strftime("%Y-%m-%d").tolist()
            chart_labels = chart_data.index.strftime("%Y-%m-%d").tolist()
        
        historical_indicators = {
            "labels": labels,
            "close": hi["Close"].tolist(),
            "rsi": hi["RSI_7"].tolist() if "RSI_7" in hi.columns else [],
            "macd": hi["MACD_12_26_9"].tolist() if "MACD_12_26_9" in hi.columns else [],
            "macdh": hi["MACDh_12_26_9"].tolist() if "MACDh_12_26_9" in hi.columns else [],
            "macds": hi["MACDs_12_26_9"].tolist() if "MACDs_12_26_9" in hi.columns else [],
            "bb_upper": hi["BBU_5_2.0_2.0"].tolist() if "BBU_5_2.0_2.0" in hi.columns else [],
            "bb_lower": hi["BBL_5_2.0_2.0"].tolist() if "BBL_5_2.0_2.0" in hi.columns else [],
            "bb_middle": hi["BBM_5_2.0_2.0"].tolist() if "BBM_5_2.0_2.0" in hi.columns else [],
            "stoch_k": hi["STOCHk_14_3_3"].tolist() if "STOCHk_14_3_3" in hi.columns else [],
            "stoch_d": hi["STOCHd_14_3_3"].tolist() if "STOCHd_14_3_3" in hi.columns else [],
        }

        historical_indicators = convert_nan_to_none(historical_indicators)
        prediction_result = convert_nan_to_none(prediction_result)

        return {
            "chartData": {
                "labels": chart_labels,
                "values": chart_data["Close"].tolist(),
            },
            "historicalIndicators": historical_indicators,
            "prediction": prediction_result,
            "indicators": {},
            "interval_type": interval_type,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unhandled error in get_stock_prediction_data: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

def get_index_pre_analysis_data(ticker: str):
    try:
        index_data = yf.Ticker(ticker)
        hist_data = index_data.history(period="1d", interval="1m")
        
        if hist_data.empty:
            print(f"No intraday data for {ticker}, trying daily data...")
            hist_data = index_data.history(period="30d", interval="1d")
            interval_type = "daily"
        else:
            interval_type = "intraday"

        if hist_data.empty:
            raise HTTPException(
                status_code=400,
                detail="Index ticker not found or data unavailable" 
            )
        
        hist_data_with_indicators = calculate_technical_indicators(hist_data.copy()) 
        chart_data = hist_data.copy()
        prediction_result = get_prediction_with_confidence(hist_data_with_indicators) 

        hi = hist_data_with_indicators 

        if interval_type == "intraday":
            labels = hi.index.strftime("%H:%M").tolist()
            chart_labels = chart_data.index.strftime("%H:%M").tolist()
        else:
            labels = hi.index.strftime("%Y-%m-%d").tolist()
            chart_labels = chart_data.index.strftime("%Y-%m-%d").tolist()
        
        historical_indicators = {
            "labels": labels,
            "close": hi["Close"].tolist(),
            "rsi": hi["RSI_7"].tolist() if "RSI_7" in hi.columns else [],
            "macd": hi["MACD_12_26_9"].tolist() if "MACD_12_26_9" in hi.columns else [],
            "macdh": hi["MACDh_12_26_9"].tolist() if "MACDh_12_26_9" in hi.columns else [],
            "macds": hi["MACDs_12_26_9"].tolist() if "MACDs_12_26_9" in hi.columns else [],
            "bb_upper": hi["BBU_5_2.0_2.0"].tolist() if "BBU_5_2.0_2.0" in hi.columns else [],
            "bb_lower": hi["BBL_5_2.0_2.0"].tolist() if "BBL_5_2.0_2.0" in hi.columns else [],
            "bb_middle": hi["BBM_5_2.0_2.0"].tolist() if "BBM_5_2.0_2.0" in hi.columns else [],
            "stoch_k": hi["STOCHk_14_3_3"].tolist() if "STOCHk_14_3_3" in hi.columns else [],
            "stoch_d": hi["STOCHd_14_3_3"].tolist() if "STOCHd_14_3_3" in hi.columns else [],
        }

        historical_indicators = convert_nan_to_none(historical_indicators)
        prediction_result = convert_nan_to_none(prediction_result)

        return {
            "chartData": {
                "labels": chart_labels,
                "values": chart_data["Close"].tolist(),
            },
            "historicalIndicators": historical_indicators,
            "prediction": prediction_result,
            "indicators": {},
            "interval_type": interval_type,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unhandled error in get_index_pre_analysis_data: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")