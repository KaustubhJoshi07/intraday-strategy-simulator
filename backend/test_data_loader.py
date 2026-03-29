import os
from app.services.data_loader import load_market_data

file_path = r"C:\mini-quant-backtester\data\raw\nifty_5min.csv"

print("Current working directory:", os.getcwd())
print("Trying to read:", file_path)
print("Exists?", os.path.exists(file_path))
print("Files in folder:", os.listdir(r"C:\mini-quant-backtester\data\raw"))

df = load_market_data(file_path)

print("Data loaded successfully!")
print("\nFirst 5 rows:")
print(df.head())

print("\nData types:")
print(df.dtypes)

print("\nShape:")
print(df.shape)