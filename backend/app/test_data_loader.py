from app.services.data_loader import load_market_data

df = load_market_data("../data/raw/nifty_5min.csv")
print(df.head())
print(df.dtypes)
print(df.shape)