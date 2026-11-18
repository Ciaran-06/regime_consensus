"""Phase 5: rebuild the signals table and family votes with the signals kept by the correlation pre-check (R03).

Builds all six signals for BTC and ETH on 2017-2025 closes, cuts to the design period, checks the family
votes use exactly the signals in config before printing any result, saves the table, and logs one run.
"""
import pandas as pd

from regime_consensus.agreement import agreement_rate, family_vote
from regime_consensus.config import DESIGN_COINS, DESIGN_END, DESIGN_START, FAMILIES
from regime_consensus.io import load_clean, save_derived
from regime_consensus.runlog import check_new_run, log_run
from regime_consensus.signals import SIGNALS, build_signals

SCRIPT = "scripts/02_signals.py"
RUN_TYPE = "diagnostic"
PHASE = "5"
PREDICTION = (
    "Predicted before running (NOTES.md R03): momentum agreement below 1.00, about 0.7; "
    "reversion agreement at most 0.21; z-score agrees on nearly every day RSI extreme votes."
)
WHAT_CHANGED = (
    "Rerun of R04 after bug fix (build_signals built the family votes from the candidate lists). "
    f"Rebuilt family votes with signals kept by R03: momentum {FAMILIES['momentum']}, reversion {FAMILIES['reversion']}. "
    f"{PREDICTION}"
)

# 0. Refuse a duplicate or over-budget run before any data is loaded
check_new_run(RUN_TYPE, SCRIPT, WHAT_CHANGED)

# 1. Load BTC and ETH closes, including the 2017 warm-up
prices = load_clean(DESIGN_COINS, columns=["close"], end=DESIGN_END)

# 2. Build on 2017-2025, then cut to the design period
signals = build_signals(prices)
signals = signals[signals["date"] >= pd.Timestamp(DESIGN_START)].reset_index(drop=True)

# 3. Checks before any result is printed: the right rows, and family votes built from the config lists
assert set(signals["coin"]) == set(DESIGN_COINS), f"coins in table: {sorted(set(signals['coin']))}"
assert not signals.duplicated(["coin", "date"]).any(), "duplicate (coin, date) rows"
for family, kept in FAMILIES.items():
    expected = family_vote(signals[[f"{name}_vote" for name in kept]])
    actual = signals[f"{family}_vote"]
    same = (actual == expected) | (actual.isna() & expected.isna())
    assert same.all(), f"{family}_vote does not match the signals in config ({kept}) on {int((~same).sum())} rows"

# 4. Missing scores in 2018 onwards (expected: 0 for every signal)
missing = {name: int(signals[f"{name}_score"].isna().sum()) for name in SIGNALS}
for name, count in missing.items():
    print(f"{name}: {count} missing scores")

# 5. Save
save_derived(signals, "signals")

# 6. Agreement rates per coin and family, and z-score agreement on RSI-extreme days
rates = []
for coin, coin_signals in signals.groupby("coin"):
    momentum = agreement_rate(coin_signals["momentum_vote"])
    reversion = agreement_rate(coin_signals["reversion_vote"])
    rsi_days = coin_signals["rsi_extreme_vote"].notna()
    z_agree = (coin_signals.loc[rsi_days, "z_score_vote"] == coin_signals.loc[rsi_days, "rsi_extreme_vote"]).mean()
    line = (
        f"{coin} momentum {momentum:.2f}, reversion {reversion:.2f}, "
        f"z-score agrees on {z_agree:.2f} of {int(rsi_days.sum())} RSI-extreme days"
    )
    print(line)
    rates.append(line)

total_missing = sum(missing.values())
summary = f"Agreement rates: {'; '.join(rates)}. Missing scores: {total_missing}."
print(summary)

# 7. Log the run
log_run(RUN_TYPE, phase=PHASE, script=SCRIPT, what_changed=WHAT_CHANGED, result=summary)