import pandas as pd


def calculate_backtest_metrics(trade_log_df: pd.DataFrame, daily_summary_df: pd.DataFrame) -> dict:
    if trade_log_df.empty:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "total_net_pnl": 0,
            "avg_trade_pnl": 0,
            "avg_win": 0,
            "avg_loss": 0,
            "profit_factor": 0,
            "max_drawdown": 0,
        }

    total_trades = len(trade_log_df)
    winning_trades = (trade_log_df["net_pnl"] > 0).sum()
    losing_trades = (trade_log_df["net_pnl"] < 0).sum()
    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0

    total_net_pnl = trade_log_df["net_pnl"].sum()
    avg_trade_pnl = trade_log_df["net_pnl"].mean()

    wins = trade_log_df.loc[trade_log_df["net_pnl"] > 0, "net_pnl"]
    losses = trade_log_df.loc[trade_log_df["net_pnl"] < 0, "net_pnl"]

    avg_win = wins.mean() if not wins.empty else 0
    avg_loss = losses.mean() if not losses.empty else 0

    gross_profit = wins.sum() if not wins.empty else 0
    gross_loss = abs(losses.sum()) if not losses.empty else 0
    profit_factor = gross_profit / gross_loss if gross_loss != 0 else 0

    if not daily_summary_df.empty:
        equity_curve = daily_summary_df["cumulative_pnl"]
        running_max = equity_curve.cummax()
        drawdown = equity_curve - running_max
        max_drawdown = drawdown.min()
    else:
        max_drawdown = 0

    return {
        "total_trades": int(total_trades),
        "winning_trades": int(winning_trades),
        "losing_trades": int(losing_trades),
        "win_rate": round(win_rate, 2),
        "total_net_pnl": round(total_net_pnl, 2),
        "avg_trade_pnl": round(avg_trade_pnl, 2),
        "avg_win": round(avg_win, 2) if pd.notna(avg_win) else 0,
        "avg_loss": round(avg_loss, 2) if pd.notna(avg_loss) else 0,
        "profit_factor": round(profit_factor, 2),
        "max_drawdown": round(max_drawdown, 2),
    }