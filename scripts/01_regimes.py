"""Phase 3: regime labels and spell count (NOTES.md section 3).

Labels the four trend states for BTC and ETH on 2017-2025 closes, cuts to the design period,
counts ties at both lookbacks, saves the labels and logs one diagnostic run.
"""
import pandas as pd

from regime_consensus.config import DESIGN_COINS, DESIGN_END, DESIGN_START, FAST_LOOKBACK, SLOW_LOOKBACK
from regime_consensus.io import load_clean, save_derived
from regime_consensus.regime_modeling import count_ties, find_spells, label_regimes, spell_summary
from regime_consensus.runlog import check_new_run, log_run

SCRIPT = "scripts/01_regimes.py"
RUN_TYPE = "diagnostic"
PHASE = "3"
WHAT_CHANGED = "Regime labels and spell count, BTC and ETH, 2018-2025"

check_new_run(RUN_TYPE, SCRIPT, WHAT_CHANGED)

coins = load_clean(DESIGN_COINS, columns=["close", "date"], end=DESIGN_END)

ties = []
for coin, coin_prices in coins.groupby("coin"):
    close = coin_prices.set_index("date")["close"].sort_index()
    for lookback in (SLOW_LOOKBACK, FAST_LOOKBACK):
        count = count_ties(close, lookback)
        print(f"{coin}, {lookback}-day ties: {count}")
        ties.append(f"{coin} {lookback}-day {count}")

labeled_coins = label_regimes(coins)
labeled_coins = labeled_coins[labeled_coins["date"] >= pd.Timestamp(DESIGN_START)].reset_index(drop=True)
save_derived(labeled_coins, "regimes")

summary_table = spell_summary(find_spells(labeled_coins))
print(summary_table)

summary = f"Ties: {'; '.join(ties)}. Spell summary: {summary_table.to_dict('records')}"

log_run(RUN_TYPE, phase=PHASE, script=SCRIPT, what_changed=WHAT_CHANGED, result=summary)