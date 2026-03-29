import pandas as pd

def add_bollinger_bands(df: pd.DataFrame, period: int = 20, multiplier: float = 2.0) -> pd.DataFrame:
    df = df.copy()
    df["bb_mid"] = df["close"].rolling(period).mean()
    df["bb_std"] = df["close"].rolling(period).std()
    df["bb_upper"] = df["bb_mid"] + multiplier * df["bb_std"]
    df["bb_lower"] = df["bb_mid"] - multiplier * df["bb_std"]
    return df