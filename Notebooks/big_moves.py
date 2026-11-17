"""DATA.md check: the largest daily moves on BTC and ETH, with two tests that separate glitches from real events.

Run from the project root:
    uv run python Notebooks/big_moves.py

For each coin, takes the TOP_N largest absolute close-to-close returns (2017-2025, warm-up included,
because the warm-up feeds the 365-day trend labels) and adds:
    other_coin_move  the other coin's return on the same day
    co_move          True if the other coin moved the same way by at least CO_MOVE_SHARE of the size
                     (real market events move both coins; a glitch on one exchange feed usually doesn't)
    next_day_move    this coin's return the next day
    reversed         True if the next day went the other way by at least REVERSAL_SHARE of the size
                     (a bad close shows up as a big move followed by a big move back)
    suspect          True if it did not co-move AND it reversed: look these up first

BTC and ETH only: design data. Never run this on the unseen coins before claim 3.
"""

import pandas as pd

from regime_consensus.config import DESIGN_COINS
from regime_consensus.io import load_clean

TOP_N = 10
CO_MOVE_SHARE = 1 / 3
REVERSAL_SHARE = 1 / 2

prices = load_clean(DESIGN_COINS, columns=["close"])

# one column of closes per coin, one row per day
closes = prices.pivot(index="date", columns="coin", values="close").sort_index()
returns = closes.pct_change()  # simple daily return: close_t / close_{t-1} - 1

if len(DESIGN_COINS) != 2:
    raise SystemExit("The co-move test assumes exactly two design coins.")

rows = []
for coin in DESIGN_COINS:
    other = next(c for c in DESIGN_COINS if c != coin)
    move = returns[coin]
    top_days = move.abs().nlargest(TOP_N).index

    for day in top_days:
        size = move.loc[day]
        other_size = returns.loc[day, other]
        next_size = move.shift(-1).loc[day]
        rows.append(
            {
                "coin": coin,
                "date": day.date(),
                "move": size,
                "other_coin_move": other_size,
                "co_move": bool(pd.notna(other_size) and other_size * size > 0
                                and abs(other_size) >= CO_MOVE_SHARE * abs(size)),
                "next_day_move": next_size,
                "reversed": bool(pd.notna(next_size) and next_size * size < 0
                                 and abs(next_size) >= REVERSAL_SHARE * abs(size)),
            }
        )

report = pd.DataFrame(rows)
report["suspect"] = ~report["co_move"] & report["reversed"]

pd.set_option("display.width", 120)
print(
    report.to_string(
        index=False,
        formatters={c: "{:+.1%}".format for c in ["move", "other_coin_move", "next_day_move"]},
    )
)
print(f"\nSuspect days (no co-move and reversed): {int(report['suspect'].sum())} of {len(report)}")