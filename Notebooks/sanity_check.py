import json
import pandas as pd

from regime_consensus import RAW, UNSEEN_COINS, DESIGN_COINS

coins = UNSEEN_COINS + DESIGN_COINS

class bcolors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

rows = []

for coin in coins:
    for file in sorted((RAW / coin).glob("*.json")):
        candles = json.loads(file.read_text())
        for candle in candles:
            time = candle[0]
            rows.append({
                "Coin": coin,
                "Time": time,
                "Midnight": time % 86400 == 0,
            })

times = pd.DataFrame(rows)

for coin, group in times.groupby("Coin"):
    if group["Midnight"].all():
        print(bcolors.OKGREEN + f"{coin}: all candles start at midnight UTC" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + f"{coin}: {(~group['Midnight']).sum()} candles do not start at midnight UTC" + bcolors.ENDC)

print(times["Time"].head())

