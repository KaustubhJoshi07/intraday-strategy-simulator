import pandas as pd
from datetime import datetime, time
from app.services.strategy_engine import (
    is_within_trade_window,
    bollinger_long_entry_signal,
    bollinger_long_exit_signal,
)


def run_bollinger_backtest(
    df: pd.DataFrame,
    stop_loss_points: float = 30,
    take_profit_points: float = 60,
    quantity: int = 20,
    max_trades_per_day: int = 2,
    trade_start_time=None,
    trade_end_time=None,
    square_off_time=None,
    cost_per_trade: float = 20,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Runs a simple long-only Bollinger mean reversion backtest.

    Returns:
        trade_log_df: trade-level log
        daily_summary_df: date-level summary
    """

    df = df.copy()
    df["date"] = df["datetime"].dt.date
    df["time"] = df["datetime"].dt.time

    trades = []

    # group day by day
    for trade_date, day_df in df.groupby("date"):
        day_df = day_df.reset_index(drop=True)

        open_trade = None
        trades_taken_today = 0

        for i in range(len(day_df) - 1):
            row = day_df.loc[i]
            next_row = day_df.loc[i + 1]

            current_time = row["time"]

            # skip rows where indicators are not available yet
            if pd.isna(row["bb_lower"]) or pd.isna(row["bb_mid"]):
                continue

            # -------------------------
            # ENTRY LOGIC
            # -------------------------
            if open_trade is None:
                if trades_taken_today >= max_trades_per_day:
                    continue

                if not is_within_trade_window(current_time, trade_start_time, trade_end_time):
                    continue

                if bollinger_long_entry_signal(row):
                    entry_price = next_row["open"]
                    entry_time = next_row["datetime"]

                    open_trade = {
                        "trade_date": trade_date,
                        "entry_time": entry_time,
                        "entry_price": float(entry_price),
                        "quantity": quantity,
                        "side": "LONG",
                        "signal_name": "BOLLINGER_LONG",
                    }

            # -------------------------
            # EXIT LOGIC
            # -------------------------
            else:
                entry_price = open_trade["entry_price"]

                stop_loss_price = entry_price - stop_loss_points
                take_profit_price = entry_price + take_profit_points

                exit_reason = None
                exit_price = None
                exit_time = row["datetime"]

                candle_low = row["low"]
                candle_high = row["high"]
                candle_close = row["close"]

                # Conservative assumption:
                # if both SL and TP hit in the same candle, assume SL hit first
                if candle_low <= stop_loss_price and candle_high >= take_profit_price:
                    exit_reason = "STOP_LOSS"
                    exit_price = stop_loss_price

                elif candle_low <= stop_loss_price:
                    exit_reason = "STOP_LOSS"
                    exit_price = stop_loss_price

                elif candle_high >= take_profit_price:
                    exit_reason = "TAKE_PROFIT"
                    exit_price = take_profit_price

                elif bollinger_long_exit_signal(row):
                    exit_reason = "BB_MID_EXIT"
                    exit_price = candle_close

                elif square_off_time is not None and current_time >= square_off_time:
                    exit_reason = "EOD_SQUARE_OFF"
                    exit_price = candle_close

                if exit_reason is not None:
                    gross_pnl = (exit_price - entry_price) * quantity
                    total_cost = cost_per_trade
                    net_pnl = gross_pnl - total_cost

                    trade_record = {
                        "trade_date": open_trade["trade_date"],
                        "entry_time": open_trade["entry_time"],
                        "exit_time": exit_time,
                        "entry_price": round(entry_price, 2),
                        "exit_price": round(exit_price, 2),
                        "quantity": quantity,
                        "side": open_trade["side"],
                        "signal_name": open_trade["signal_name"],
                        "exit_reason": exit_reason,
                        "gross_pnl": round(gross_pnl, 2),
                        "cost": round(total_cost, 2),
                        "net_pnl": round(net_pnl, 2),
                    }

                    trades.append(trade_record)
                    open_trade = None
                    trades_taken_today += 1

        # force close at end of day if still open
        if open_trade is not None:
            last_row = day_df.iloc[-1]

            entry_price = open_trade["entry_price"]
            exit_price = float(last_row["close"])
            exit_time = last_row["datetime"]

            gross_pnl = (exit_price - entry_price) * quantity
            total_cost = cost_per_trade
            net_pnl = gross_pnl - total_cost

            trade_record = {
                "trade_date": open_trade["trade_date"],
                "entry_time": open_trade["entry_time"],
                "exit_time": exit_time,
                "entry_price": round(entry_price, 2),
                "exit_price": round(exit_price, 2),
                "quantity": quantity,
                "side": open_trade["side"],
                "signal_name": open_trade["signal_name"],
                "exit_reason": "FORCED_EOD_EXIT",
                "gross_pnl": round(gross_pnl, 2),
                "cost": round(total_cost, 2),
                "net_pnl": round(net_pnl, 2),
            }

            trades.append(trade_record)

    trade_log_df = pd.DataFrame(trades)

    if trade_log_df.empty:
        daily_summary_df = pd.DataFrame(
            columns=["trade_date", "trades_count", "gross_pnl", "cost", "net_pnl", "cumulative_pnl"]
        )
        return trade_log_df, daily_summary_df

    daily_summary_df = (
        trade_log_df.groupby("trade_date", as_index=False)
        .agg(
            trades_count=("net_pnl", "count"),
            gross_pnl=("gross_pnl", "sum"),
            cost=("cost", "sum"),
            net_pnl=("net_pnl", "sum"),
        )
        .sort_values("trade_date")
        .reset_index(drop=True)
    )

    daily_summary_df["cumulative_pnl"] = daily_summary_df["net_pnl"].cumsum()

    return trade_log_df, daily_summary_df