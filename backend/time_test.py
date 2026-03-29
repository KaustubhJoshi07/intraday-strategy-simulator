from app.services.data_loader import load_market_data

file_path = r"C:\mini-quant-backtester\data\raw\nifty_5min.csv"
df = load_market_data(file_path)

print(df["datetime"].min())
print(df["datetime"].max())

df["date"] = df["datetime"].dt.date
df["time"] = df["datetime"].dt.time

sample_day = df[df["date"] == df["date"].iloc[0]].copy()
print(sample_day[["datetime", "open", "high", "low", "close"]].head(20))
print(sample_day[["datetime", "open", "high", "low", "close"]].tail(20))