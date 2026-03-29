from pydantic import BaseModel


class BacktestRequest(BaseModel):
    stop_loss_points: float = 30
    take_profit_points: float = 60
    quantity: int = 20
    max_trades_per_day: int = 2
    cost_per_trade: float = 20
    bollinger_period: int = 20
    bollinger_multiplier: float = 2
    rows_limit: int = 5000