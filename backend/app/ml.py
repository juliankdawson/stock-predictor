import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score

def load_data(ticker: str) -> pd.DataFrame:
    df = yf.Ticker(ticker).history(period="max")
    df.index = pd.to_datetime(df.index)

    # Drop columns we don't use
    df = df.drop(columns=["Dividends", "Stock Splits"], errors="ignore")

    if df.empty:
        raise ValueError("No data returned for ticker")

    return df

def add_target(df: pd.DataFrame) -> pd.DataFrame:
    df["Tomorrow"] = df["Close"].shift(-1)
    df["Target"] = (df["Tomorrow"] > df["Close"]).astype(int)

    # Avoid very old market regimes
    df = df.loc["1990-01-01":].copy()

    return df

def add_features(df: pd.DataFrame, horizons=None):
    if horizons is None:
        horizons = [2, 5, 60, 250, 1000]

    new_predictors = []

    for horizon in horizons:
        rolling_avg = df["Close"].rolling(horizon).mean()

        ratio_col = f"Close_Ratio_{horizon}"
        trend_col = f"Trend_{horizon}"

        df[ratio_col] = df["Close"] / rolling_avg
        df[trend_col] = df["Target"].shift(1).rolling(horizon).sum()

        new_predictors.extend([ratio_col, trend_col])

    df = df.dropna()

    return df, new_predictors

def create_model():
    return RandomForestClassifier(
        n_estimators=200,
        min_samples_split=50,
        random_state=1
    )

def predict(train, test, predictors, model):
    model.fit(train[predictors], train["Target"])

    probs = model.predict_proba(test[predictors])[:, 1]
    preds = (probs >= 0.6).astype(int)

    return pd.Series(preds, index=test.index, name="Prediction")

def backtest(df, model, predictors, start=2500, step=250):
    all_preds = []

    for i in range(start, df.shape[0], step):
        train = df.iloc[:i]
        test = df.iloc[i:i + step]

        preds = predict(train, test, predictors, model)
        all_preds.append(preds)

    return pd.concat(all_preds)

def run_pipeline(ticker: str):
    df = load_data(ticker)
    df = add_target(df)
    df, predictors = add_features(df)

    model = create_model()
    predictions = backtest(df, model, predictors)

    precision = precision_score(
        df.loc[predictions.index, "Target"],
        predictions
    )

    # Take the last 30 predictions
    latest_preds = predictions.tail(30)

    # Convert for JSON
    latest_predictions = {
        k.strftime("%Y-%m-%d"): int(v) for k, v in latest_preds.items()
    }

    return {
        "ticker": ticker,
        "precision": round(precision, 3),
        "latest_predictions": latest_predictions
    }