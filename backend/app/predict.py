from fastapi import APIRouter, HTTPException
from ml import run_pipeline

router = APIRouter()

@router.get("/predict/{ticker}")
def predict(ticker: str):
    try:
        return run_pipeline(ticker.upper())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))