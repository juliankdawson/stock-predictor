from fastapi import APIRouter, HTTPException
from app.ml import load_data

router = APIRouter()

@router.get("/history/{ticker}")
def get_history(ticker: str, days: int = 365):
    try:
        df = load_data(ticker)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    df_recent = df.tail(days)[["Open", "High", "Low", "Close", "Volume"]]

    history = {
        date.strftime("%Y-%m-%d"): row.to_dict()
        for date, row in df_recent.iterrows()
    }

    return {"ticker": ticker, "history": history}