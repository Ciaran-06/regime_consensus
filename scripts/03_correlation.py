"""Phase 5: correlation pre-check (NOTES.md section 4).

Spearman correlations of the six signal scores per coin, on all days, calm days
and turbulent days. Applies select_signals to the all-days tables only.
Saves the correlation tables and volatility labels, and logs one diagnostic run.
"""
import pandas as pd

from regime_consensus.config import (DESIGN_COINS, DESIGN_END, DESIGN_START,
                                     MOMENTUM_PRIORITY, REVERSION_PRIORITY,
                                     VOLATILITY_REGIMES)
from regime_consensus.io import load_clean, load_derived, save_derived
from regime_consensus.regime_modeling import label_volatility
from regime_consensus.runlog import log_run
from regime_consensus.signal_selection import select_signals
from regime_consensus.signals import SIGNALS

PREDICTION = "Predicted before running: Bollinger dropped as a near-copy of z-score; other pairs not predicted."

signals = load_derived("signals")
pre_merge_len = len(signals)

prices = load_clean(columns=["close"], coins=DESIGN_COINS, end=DESIGN_END)

volatility_frames = []
for coin, price in prices.groupby("coin"):
    price = price.set_index("date").sort_index()
    volatility = label_volatility(price["close"])
    volatility_frames.append(pd.DataFrame({"coin": coin, "date": price.index, "volatility": volatility.values}))

volatility_labels = pd.concat(volatility_frames, ignore_index=True)
volatility_labels = volatility_labels[volatility_labels["date"] >= pd.Timestamp(DESIGN_START)]
volatility_labels = volatility_labels.reset_index(drop=True)

save_derived(volatility_labels, "volatility")

signals = signals.merge(volatility_labels, on=["coin", "date"], how="left")
assert len(signals) == pre_merge_len

rename = {f"{name}_score": name for name in SIGNALS}
score_columns = list(rename)

correlations = {"all": {}, "calm": {}, "turbulent": {}}
period_days = {}

for coin, coin_signals in signals.groupby("coin"):
    correlations["all"][coin] = coin_signals[score_columns].rename(columns=rename).corr(method="spearman")
    period_days[coin] = {"all": len(coin_signals)}

    for label, period in VOLATILITY_REGIMES.items():
        filtered_rows = coin_signals[coin_signals["volatility"] == label]
        correlations[period][coin] = filtered_rows[score_columns].rename(columns=rename).corr(method="spearman")
        period_days[coin][period] = len(filtered_rows)

kept_momentum = select_signals(correlations["all"], priority=MOMENTUM_PRIORITY)
kept_reversion = select_signals(correlations["all"], priority=REVERSION_PRIORITY)

families = [
    ("momentum", MOMENTUM_PRIORITY, kept_momentum),
    ("reversion", REVERSION_PRIORITY, kept_reversion),
]

dropped_signals = []
for family, priority, kept in families:
    dropped = [item for item in priority if item not in kept]
    dropped_signals.extend(dropped)
    print(f"=========== {family} ===========")
    print(f"Kept:    {kept}")
    print(f"Dropped: {dropped if dropped else 'none'}")

for period, tables in correlations.items():
    for coin, table in tables.items():
        print(f"============= {period} / {coin} =============")
        print(f"Days: {period_days[coin][period]}")
        print(table.round(2))

correlation_frames = []
for period, tables in correlations.items():
    for coin, table in tables.items():
        pairs = table.stack().reset_index()
        pairs.columns = ["signal_a", "signal_b", "rho"]
        pairs.insert(0, "period", period)
        pairs.insert(0, "coin", coin)
        correlation_frames.append(pairs)

correlation_table = pd.concat(correlation_frames, ignore_index=True)
save_derived(correlation_table, "correlations")

bollinger_z = "; ".join(
    f"{coin} {tables_coin.loc['bollinger', 'z_score']:.2f}"
    for coin, tables_coin in correlations["all"].items()
)
summary = (
    f"Momentum kept {kept_momentum}; reversion kept {kept_reversion}; "
    f"dropped {dropped_signals if dropped_signals else 'none'}. "
    f"Bollinger-z_score correlation (all days): {bollinger_z}."
)
print(summary)

log_run(
    "diagnostic",
    phase="5",
    script="scripts/03_correlation.py",
    what_changed=f"Correlation pre-check on six signal scores, BTC and ETH, 2018-2025. {PREDICTION}",
    result=summary,
)