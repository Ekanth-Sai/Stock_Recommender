from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
import asyncio
import datetime
import pandas as pd
from app.data_fetcher import fetch_latest_price, fetch_historical_data
from app.features import add_techincal_indicators
import joblib 
import os

from app.features import add_techincal_indicators, simple_signal

app = FastAPI()

MODEL = joblib.load(os.path.join(os.path.dirname(__file__), "model.joblib"))
FEATURES = ['rsi_14', 'sma_20', 'sma_50', 'macd', 'macd_signal', 'atr_14', 'volume', 'Return_1d']

def make_features_from_latest(df_latest: pd.DataFrame):
    df_feat = add_techincal_indicators(df_latest)

    row = df_feat.iloc[-1]
    X = row[FEATURES].to_frame().T

    return X

@app.get("/api/recommend")
async def recommend(ticker: str = "INFY.NS"):
    df = fetch_historical_data(ticker, period="60d", interval="1d")
    df = add_techincal_indicators(df)

    last = df.dropna(subset = FEATURES).iloc[-1]
    X = last[FEATURES].to_frame().T
    probs = MODEL.predict_proba(X)[0]
    classes = MODEL.classes_
    ml_pred = classes[probs.argmax()]
    ml_conf = float(probs.max())

    rule_pred = simple_signal(last)

    return JSONResponse({
        "ticker": ticker,
        "ml_prediction": ml_pred,
        "ml_confidence": ml_conf,
        "ml_probs": dict(zip(classes, probs)),
        "rule_prediction": rule_pred
    })

@app.websocket("/ws/realtime/{ticker}")
async def websocket_realtime(ws: WebSocket, ticker: str):
    await ws.accept()
    try:
        while True:
            df = fetch_historical_data(ticker, period="7d", interval="1m")

            if df is None or df.empty:
                await asyncio.sleep(60)
                continue

            df_feat = add_techincal_indicators(df)
            df_feat = df_feat.dropna(subset=FEATURES)

            if df_feat.empty:
                await asyncio.sleep(60)
                continue

            X = df_feat[FEATURES].iloc[-1:].copy()
            probs = MODEL.predict_proba(X)[0]
            classes = MODEL.classes_
            ml_pred = classes[probs.argmax()]
            ml_conf = float(probs.max())

            last_row = df_feat.iloc[-1]
            rule_pred = simple_signal(last_row)

            ts = df_feat.index[-1].isoformat()

            payload = {
                "timestamp": ts,
                "ticker": ticker,
                "close": float(df_feat['close'].iloc[-1]),
                "features": X.iloc[0].to_dict(),
                "ml_prediction": ml_pred,
                "ml_confidence": ml_conf,
                "ml_probs": dict(zip(classes, probs)),
                "rule_prediction": rule_pred
            }

            await ws.send_json(payload)
            await asyncio.sleep(60)
    except Exception as e:
        await ws.close()