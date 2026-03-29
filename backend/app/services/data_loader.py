import pandas as pd

def load_market_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)

    required_cols = ["datetime", "open", "high", "low", "close", "volume", "instrument"]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    df["datetime"] = pd.to_datetime(
        df["datetime"],
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce"
)

    # shift timestamps by 2 hours 50 minutes
    df["datetime"] = df["datetime"] + pd.Timedelta(hours=2, minutes=50)

    numeric_cols = ["open", "high", "low", "close", "volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["datetime", "open", "high", "low", "close", "volume"])

    return df