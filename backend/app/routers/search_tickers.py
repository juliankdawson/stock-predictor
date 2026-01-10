from fastapi import APIRouter, Query, HTTPException
import requests

router = APIRouter(prefix="/search", tags=["search"])

YAHOO_SEARCH_URL = "https://query1.finance.yahoo.com/v1/finance/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

@router.get("/tickers")
def search_tickers(
    query: str = Query(..., min_length=1),
    limit: int = 10
):
    params = {
        "q": query,
        "quotesCount": limit,
        "newsCount": 0
    }

    response = requests.get(
        YAHOO_SEARCH_URL,
        params=params,
        headers=HEADERS,
        timeout=5
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Yahoo Finance search failed"
        )

    data = response.json()
    quotes = data.get("quotes", [])

    results = []
    for q in quotes:
        if "symbol" in q:
            results.append({
                "ticker": q.get("symbol"),
                "name": q.get("shortname") or q.get("longname"),
                "exchange": q.get("exchange"),
                "type": q.get("quoteType"),
            })

    return results
