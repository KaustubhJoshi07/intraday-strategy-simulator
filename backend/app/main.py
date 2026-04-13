from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.backtest import router as backtest_router
import os

app = FastAPI(title="Mini Quant Backtester API")
print("API HIT")
print("Incoming file path:", file_path)
print("Current working dir:", os.getcwd()) 

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://intraday-strategy-sim.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(backtest_router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Mini Quant Backtester API is running"}