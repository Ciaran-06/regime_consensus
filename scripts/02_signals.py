
import pandas as pd

from regime_consensus.agreement import agreement_rate
from regime_consensus.config import DESIGN_COINS, DESIGN_END, DESIGN_START
from regime_consensus.io import load_clean, save_derived
from regime_consensus.runlog import log_run
from regime_consensus.signals import SIGNALS, build_signals

PREDICTION = "Predicted before running: momentum agreement above 0.9, reversion below 0.3 (NOTES.md section 6)."

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
    print(f"{coin}: momentum {momentum:.2f}, reversion {reversion:.2f}")
    rates.append(f"{coin} momentum {momentum:.2f}, reversion {reversion:.2f}")

total_missing = sum(missing.values())
summary = f"Agreement rates: {'; '.join(rates)}. Missing scores: {total_missing}."
print(summary)

# 7. Log the run
log_run(
    "diagnostic",
    phase="4",
    script="scripts/02_signals.py",
    what_changed=f"Built six signals and family votes, BTC and ETH, 2018-2025. {PREDICTION}",
    result=summary,
)