from fastapi import APIRouter, HTTPException
from app.ml import load_data, add_target, add_features, create_model, backtest
from sklearn.metrics import precision_score

router = APIRouter()

@router.get("/metrics/{ticker}")
def get_metrics(ticker: str):
    try:
        df = load_data(ticker)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    df = add_target(df)
    df, predictors = add_features(df)
    model = create_model()
    preds = backtest(df, model, predictors)

    precision = precision_score(df.loc[preds.index, "Target"], preds)
    distribution = preds.value_counts(normalize=True).to_dict()

    return {
        "ticker": ticker,
        "precision": round(precision, 3),
        "distribution": {int(k): round(v, 3) for k, v in distribution.items()}
    }