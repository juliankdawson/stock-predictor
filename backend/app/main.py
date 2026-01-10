from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import predict, history, metrics, search_tickers

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(predict.router)
app.include_router(history.router)
app.include_router(metrics.router)
app.include_router(search_tickers.router)

@app.get("/health")
async def health():
    return {"status": "ok"}