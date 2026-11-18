
import pandas as pd

from regime_consensus.agreement import agreement_rate
from regime_consensus.config import DESIGN_COINS, DESIGN_END, DESIGN_START, MOMENTUM_SIGNALS, REVERSION_SIGNALS
from regime_consensus.io import load_clean, save_derived
from regime_consensus.runlog import log_run
from regime_consensus.signals import SIGNALS, build_signals

PREDICTION = "Predicted before running (NOTES.md R03): momentum agreement below 1.00, about 0.7; reversion agreement at most 0.21; z-score agrees on nearly every day RSI extreme votes."
# 1. Load BTC and ETH closes, including the 2017 warm-up
prices = load_clean(DESIGN_COINS, columns=["close"], end=DESIGN_END)

# 2-3. Build on 2017-2025, then cut to the design period
signals = build_signals(prices)
signals = signals[signals["date"] >= pd.Timestamp(DESIGN_START)].reset_index(drop=True)

# 4. Missing scores in 2018 onwards (expected: 0 for every signal)
missing = {name: int(signals[f"{name}_score"].isna().sum()) for name in SIGNALS}
for name, count in missing.items():
    print(f"{name}: {count} missing scores")

# 5. Save
save_derived(signals, "signals")

# 6. Agreement rates per coin and family
rates = []
for coin, coin_signals in signals.groupby("coin"):
    momentum = agreement_rate(coin_signals["momentum_vote"])
    reversion = agreement_rate(coin_signals["reversion_vote"])
    rsi_days = coin_signals["rsi_extreme_vote"].notna()
    z_agree = (coin_signals.loc[rsi_days, "z_score_vote"] == coin_signals.loc[rsi_days, "rsi_extreme_vote"]).mean()
    print(f"{coin}: z-score agrees on {z_agree:.2f} of {rsi_days.sum()} RSI-extreme days")
    print(f"{coin}: momentum {momentum:.2f}, reversion {reversion:.2f}")
    rates.append(f"{coin} momentum {momentum:.2f}, reversion {reversion:.2f}, z-score agrees on {z_agree:.2f} of {rsi_days.sum()} RSI-extreme days")

total_missing = sum(missing.values())
summary = f"Agreement rates: {'; '.join(rates)}. Missing scores: {total_missing}."
print(summary)

# 7. Log the run
log_run(
    "diagnostic",
    phase="5",
    script="scripts/02_signals.py",
    what_changed=f"Rebuilt family votes with signals kept by R03: momentum {MOMENTUM_SIGNALS}, reversion {REVERSION_SIGNALS}. {PREDICTION}",
    result=summary,
)