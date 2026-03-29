from datetime import time


def is_within_trade_window(current_time, start_time, end_time) -> bool:
    if start_time is None or end_time is None:
        return True
    return start_time <= current_time <= end_time


def bollinger_long_entry_signal(row) -> bool:
    """
    Entry condition:
    Close is below lower Bollinger Band
    """
    if row["close"] < row["bb_lower"]:
        return True
    return False


def bollinger_long_exit_signal(row) -> bool:
    """
    Exit condition:
    Close comes back to or above middle Bollinger Band
    """
    if row["close"] >= row["bb_mid"]:
        return True
    return False