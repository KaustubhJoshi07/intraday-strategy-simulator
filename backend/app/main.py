from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.backtest import router as backtest_router

app = FastAPI(title="Mini Quant Backtester API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TEMP FIX
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(backtest_router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Mini Quant Backtester API is running"}