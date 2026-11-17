import pandas as pd

from regime_consensus import UNSEEN, UNSEEN_COINS

frames = []

for coin in UNSEEN_COINS:
    df = pd.read_parquet(UNSEEN / f"{coin}.parquet",columns=["date"])
    print(f"{coin} has {df.shape[0]} rows")
    df["coin"] = coin
    frames.append(df)

data = pd.concat(frames, ignore_index=True)

print("Total number of rows:    ", data.shape[0])

bch = data[data["coin"] == "BCH-USD"]
calender = pd.date_range(start=bch["date"].min(),end=bch["date"].max(),freq="D")

missing = ~calender.isin(bch["date"])
print(calender[missing])