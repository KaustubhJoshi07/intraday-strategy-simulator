from app.services.data_loader import load_market_data
from app.services.indicator_engine import add_bollinger_bands
from app.services.backtest_engine import run_bollinger_backtest
from app.services.metrics_engine import calculate_backtest_metrics

file_path = r"C:\mini-quant-backtester\data\raw\nifty_5min.csv"

# 1. Load data
df = load_market_data(file_path)

# 2. Optional: reduce data size for faster testing first
df = df.tail(5000).copy()

# 3. Add indicators
df = add_bollinger_bands(df, period=20, multiplier=2)

# 4. Run backtest
trade_log_df, daily_summary_df = run_bollinger_backtest(
    df=df,
    stop_loss_points=30,
    take_profit_points=60,
    quantity=20,
    max_trades_per_day=2,
    cost_per_trade=20,
    trade_start_time=None,
    trade_end_time=None,
    square_off_time=None,
)

metrics = calculate_backtest_metrics(trade_log_df, daily_summary_df)

print("\n=== METRICS ===")
for key, value in metrics.items():
    print(f"{key}: {value}")

print("\n=== TRADE LOG ===")
print(trade_log_df.head(10))

print("\n=== DAILY SUMMARY ===")
print(daily_summary_df.head(10))

print("\nTotal trades:", len(trade_log_df))

if not daily_summary_df.empty:
    print("Total net pnl:", round(daily_summary_df["net_pnl"].sum(), 2))
    print("Final cumulative pnl:", round(daily_summary_df["cumulative_pnl"].iloc[-1], 2))
else:
    print("No trades generated.")