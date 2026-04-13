import yfinance as yf
import pandas as pd

symbol = "NIFTYBEES.NS"  # ETF (has volume)

# Get last 60 days (max for 5-min)
data = yf.download(symbol, interval="5m", period="60d")

# Reset index
data = data.reset_index()

# Rename columns (match your backend format)
data.rename(columns={
    "Datetime": "datetime",
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Volume": "volume"
}, inplace=True)

# Keep only needed columns
data = data[["datetime", "open", "high", "low", "close", "volume"]]

# Optional: remove timezone (cleaner for your app)
data["datetime"] = data["datetime"].dt.tz_localize(None)

# Save file
data.to_csv(r"C:\Users\kjosh\Downloads\nifty_5min_2months.csv", index=False)

print("✅ 2 months data saved successfully")