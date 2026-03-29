from pathlib import Path
from fastapi import APIRouter
from app.models.request_models import BacktestRequest
from app.services.data_loader import load_market_data
from app.services.indicator_engine import add_bollinger_bands
from app.services.backtest_engine import run_bollinger_backtest
from app.services.metrics_engine import calculate_backtest_metrics

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = BASE_DIR / "data" / "nifty_5min.csv"


@router.post("/run-backtest")
def run_backtest(request: BacktestRequest):
    df = load_market_data(str(DATA_FILE))

    if request.rows_limit:
        df = df.tail(request.rows_limit).copy()

    df = add_bollinger_bands(
        df,
        period=request.bollinger_period,
        multiplier=request.bollinger_multiplier,
    )

    trade_log_df, daily_summary_df = run_bollinger_backtest(
        df=df,
        stop_loss_points=request.stop_loss_points,
        take_profit_points=request.take_profit_points,
        quantity=request.quantity,
        max_trades_per_day=request.max_trades_per_day,
        cost_per_trade=request.cost_per_trade,
    )

    metrics = calculate_backtest_metrics(trade_log_df, daily_summary_df)

    return {
        "metrics": metrics,
        "trade_log": trade_log_df.to_dict(orient="records"),
        "daily_summary": daily_summary_df.to_dict(orient="records"),
    }