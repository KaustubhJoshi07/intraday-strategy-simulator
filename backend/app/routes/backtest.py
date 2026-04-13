from pathlib import Path
from fastapi import APIRouter
from app.models.request_models import BacktestRequest
from app.services.data_loader import load_market_data
from app.services.indicator_engine import add_bollinger_bands
from app.services.backtest_engine import run_bollinger_backtest
from app.services.metrics_engine import calculate_backtest_metrics
from app.services.ai_summary import generate_ai_summary

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = BASE_DIR / "data" / "raw" / "nifty_5min.csv"


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

    try:
        ai_summary = generate_ai_summary({
            "total_trades": metrics.get("total_trades"),
            "win_rate": metrics.get("win_rate"),
            "total_net_pnl": metrics.get("total_net_pnl"),
            "profit_factor": metrics.get("profit_factor"),
            "max_drawdown": metrics.get("max_drawdown"),
            "avg_win": metrics.get("avg_win"),
            "avg_loss": metrics.get("avg_loss"),
        })
    except Exception as e:
        ai_summary = f"AI summary unavailable: {str(e)}"

    return {
        "metrics": metrics,
        "trade_log": trade_log_df.to_dict(orient="records"),
        "daily_summary": daily_summary_df.to_dict(orient="records"),
        "ai_summary": ai_summary,
    }