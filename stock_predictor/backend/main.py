from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services import get_stock_prediction_data, get_index_pre_analysis_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/stock/{ticker}")
async def get_stock_data(ticker: str):
    try:
        return get_stock_prediction_data(ticker)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unhandled error in get_stock_data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/index/{ticker}")
async def get_index_data(ticker: str):
    try:
        return get_index_pre_analysis_data(ticker)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unhandled error in get_index_data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")