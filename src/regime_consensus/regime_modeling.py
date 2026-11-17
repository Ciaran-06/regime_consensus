"""Regime labels and spells (NOTES.md section 3).

    trend_sign(close, lookback, tie_sign)   +1 / -1 trend over the past `lookback` days, NaN in the warm-up
    count_ties(close, lookback)             how many days had a return of exactly zero (for DATA.md)
    label_state(slow, fast)                 one day's pair of signs -> BULL / BEAR / CORRECTION / REBOUND
    label_regimes(prices)                   daily labels for every coin: coin, date, slow, fast, state
    find_spells(labels)                     one row per spell: coin, state, start, end, days
    spell_summary(spells, min_days, min_spells)
                                            per coin and state: days, spells, long spells, median length,
                                            and whether the state meets the minimum evidence rule

Every number comes from config.py, so the spec and the code cannot drift apart.
"""

from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd

from regime_consensus.config import (
    FAST_LOOKBACK,
    MIN_SPELL_DAYS,
    MIN_SPELLS,
    SLOW_LOOKBACK,
    TIE_SIGN,
)

State = Literal["BULL", "BEAR", "CORRECTION", "REBOUND"]

_STATE_MAP: dict[tuple[int, int], State] = {
    (1, 1): "BULL",         # long and short trends both up
    (-1, -1): "BEAR",       # long and short trends both down
    (1, -1): "CORRECTION",  # long-term up, short-term down: a pullback
    (-1, 1): "REBOUND",     # long-term down, short-term up: a bounce
}


# ------------------------------------------------------------------ trend signs

def _check_daily_index(close: pd.Series) -> None:
    """A row shift only equals a day shift if there is exactly one row per day."""
    if not isinstance(close.index, pd.DatetimeIndex) or not close.index.is_monotonic_increasing:
        raise ValueError("close must be indexed by date, oldest first.")
    steps = close.index.to_series().diff().dropna()
    if not steps.eq(pd.Timedelta(days=1)).all():
        raise ValueError("close has missing or duplicate days, so a row shift would not equal a day shift.")


def trend_sign(close: pd.Series, lookback: int, tie_sign: int) -> pd.Series:
    """Sign of the return over the past `lookback` days, one value per day.

    +1 if today's close is above the close `lookback` days ago, -1 if below.
    A return of exactly zero gets `tie_sign` (the rule written in NOTES.md).
    NaN for the first `lookback` days, where there is not enough history.

    `close` must be one coin's closes, indexed by date, with no missing days.
    """
    if tie_sign not in (-1, 1):
        raise ValueError("tie_sign must be -1 or 1.")
    _check_daily_index(close)

    past_return = close / close.shift(lookback) - 1
    sign = np.sign(past_return)                 # +1, -1, 0, or NaN where there is no history
    sign = sign.where(sign != 0, tie_sign)      # replace exact zeros by the tie rule
    return sign.where(past_return.notna())      # keep the warm-up days as NaN


def count_ties(close: pd.Series, lookback: int) -> int:
    """Number of days whose return over `lookback` days was exactly zero (expected: 0)."""
    _check_daily_index(close)
    past_return = close / close.shift(lookback) - 1
    return int((past_return == 0).sum())


# ------------------------------------------------------------------ states

def label_state(slow: float, fast: float) -> State | None:
    """The state for one day's pair of signs, or None if either is missing (warm-up)."""
    if pd.isna(slow) or pd.isna(fast):
        return None
    return _STATE_MAP[(int(slow), int(fast))]


def label_regimes(prices: pd.DataFrame) -> pd.DataFrame:
    """Daily regime labels for every coin in `prices`.

    `prices` needs columns coin, date, close (as returned by load_clean).
    Returns coin, date, slow, fast, state. Warm-up days have NaN signs and no state.
    Each coin is labelled from its own prices only.
    """
    frames = []
    for coin, coin_prices in prices.groupby("coin"):
        close = coin_prices.set_index("date")["close"].sort_index()

        labels = pd.DataFrame(
            {
                "slow": trend_sign(close, SLOW_LOOKBACK, TIE_SIGN),
                "fast": trend_sign(close, FAST_LOOKBACK, TIE_SIGN),
            }
        )
        labels["state"] = [label_state(s, f) for s, f in zip(labels["slow"], labels["fast"])]
        labels.insert(0, "coin", coin)
        frames.append(labels.reset_index())

    return pd.concat(frames, ignore_index=True)[["coin", "date", "slow", "fast", "state"]]


# ------------------------------------------------------------------ spells

def find_spells(labels: pd.DataFrame) -> pd.DataFrame:
    """One row per spell: a continuous run of days in the same state, within one coin.

    `labels` is the output of label_regimes (after any date cut).
    Days with no state (warm-up) are left out and never join two spells together.
    Returns coin, state, start, end, days.
    """
    labelled = labels.dropna(subset=["state"]).sort_values(["coin", "date"]).copy()

    previous_state = labelled.groupby("coin")["state"].shift(1)
    previous_date = labelled.groupby("coin")["date"].shift(1)

    # A spell starts when the state changes, at a coin's first labelled day,
    # or after a gap in the dates (so an unlabelled stretch always breaks a spell).
    new_spell = (
        (labelled["state"] != previous_state)
        | previous_state.isna()
        | (labelled["date"] - previous_date != pd.Timedelta(days=1))
    )
    labelled["spell_id"] = new_spell.cumsum()

    spells = (
        labelled.groupby(["coin", "spell_id"])
        .agg(state=("state", "first"), start=("date", "min"), end=("date", "max"), days=("date", "size"))
        .reset_index()
        .drop(columns="spell_id")
    )
    return spells[["coin", "state", "start", "end", "days"]]


def spell_summary(
    spells: pd.DataFrame,
    min_days: int = MIN_SPELL_DAYS,
    min_spells: int = MIN_SPELLS,
) -> pd.DataFrame:
    """Per coin and state: total days, all spells, spells of at least `min_days`, median length,
    and whether the state meets the minimum evidence rule (at least `min_spells` long spells).
    """
    summary = (
        spells.assign(is_long=spells["days"] >= min_days)
        .groupby(["coin", "state"])
        .agg(
            total_days=("days", "sum"),
            spells=("days", "size"),
            long_spells=("is_long", "sum"),
            median_days=("days", "median"),
        )
        .reset_index()
    )
    summary["meets_minimum"] = summary["long_spells"] >= min_spells
    return summary