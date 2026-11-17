from regime_consensus.config import DESIGN_COINS, UNSEEN_COINS
from regime_consensus.io import load_clean

df = load_clean(DESIGN_COINS + UNSEEN_COINS, columns=["volume","date"])
df = df[df["volume"] == 0]
print(df)