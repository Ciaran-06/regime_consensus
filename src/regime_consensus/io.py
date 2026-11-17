"""Reading and writing project data. Every script loads and saves through here, never by building paths by hand.

    load_raw(coins, columns=None)                          raw API candles, as downloaded
    load_clean(coins, columns=None, start=None, end=None)  clean daily tables (design or unseen folder)
    save_clean(table, coin)                                writes one coin's clean table to the right folder
    load_derived(name, columns=None)                       processed tables (labels, signals, ...)
    save_derived(table, name)                              writes a processed table

Guards (NOTES.md sections 5 and 7):
    - Unseen coins only return dates (and volume) unless unlock_unseen=True is passed.
      Set it only for the claim 3 confirmatory run, and log that run in runs.csv.
    - Frozen data has no loader. It is opened once, by its own script, at the end.
    - An unknown coin raises an error instead of returning an empty table.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import date

import pandas as pd

from regime_consensus.config import DERIVED, DESIGN, DESIGN_COINS, RAW, UNSEEN, UNSEEN_COINS

RAW_FIELDS = ["time", "low", "high", "open", "close", "volume"]  # order the Coinbase API returns
CLEAN_FIELDS = ["date", "open", "high", "low", "close", "volume"]

UNSEEN_SAFE_RAW = {"time", "volume"}    # no prices
UNSEEN_SAFE_CLEAN = {"date", "volume"}  # no prices


# ------------------------------------------------------------------ helpers

def _as_list(coins: str | Iterable[str]) -> list[str]:
    """Accept one coin ("BTC-USD") or several (["BTC-USD", "ETH-USD"])."""
    return [coins] if isinstance(coins, str) else list(coins)


def _group(coin: str) -> str:
    """Which folder a coin belongs to: 'design' or 'unseen'."""
    if coin in DESIGN_COINS:
        return "design"
    if coin in UNSEEN_COINS:
        return "unseen"
    raise ValueError(f"Unknown coin {coin!r}. Add it to DESIGN_COINS or UNSEEN_COINS in config.py first.")


def _check_unseen(coin: str, columns: list[str], safe: set[str], unlock_unseen: bool) -> None:
    """Refuse to return unseen-coin prices unless explicitly unlocked."""
    if _group(coin) == "unseen" and not unlock_unseen:
        blocked = set(columns) - safe
        if blocked:
            raise PermissionError(
                f"{coin} is an unseen coin: only {sorted(safe)} can be loaded before claim 3. "
                f"Blocked: {sorted(blocked)}. Pass unlock_unseen=True only for the claim 3 confirmatory run."
            )


# ------------------------------------------------------------------ raw

def load_raw(
    coins: str | Iterable[str],
    columns: list[str] | None = None,
    unlock_unseen: bool = False,
) -> pd.DataFrame:
    """Raw candles exactly as downloaded, one row per candle, with a 'coin' column first.

    Nothing is sorted, deduplicated or converted: 'time' stays in Unix seconds.
    """
    columns = RAW_FIELDS if columns is None else list(columns)
    unknown = set(columns) - set(RAW_FIELDS)
    if unknown:
        raise ValueError(f"Unknown raw columns {sorted(unknown)}. Choose from {RAW_FIELDS}.")

    frames = []
    for coin in _as_list(coins):
        _check_unseen(coin, columns, UNSEEN_SAFE_RAW, unlock_unseen)
        files = sorted((RAW / coin).glob("*.json"))
        if not files:
            raise FileNotFoundError(f"No raw files for {coin} in {RAW / coin}. Run scripts/00_download.py first.")

        rows = []
        for file in files:
            rows.extend(json.loads(file.read_text()))
        table = pd.DataFrame(rows, columns=RAW_FIELDS)[columns]
        table.insert(0, "coin", coin)
        frames.append(table)

    return pd.concat(frames, ignore_index=True)


# ------------------------------------------------------------------ clean

def load_clean(
    coins: str | Iterable[str],
    columns: list[str] | None = None,
    start: date | str | None = None,
    end: date | str | None = None,
    unlock_unseen: bool = False,
) -> pd.DataFrame:
    """Clean daily tables, one row per coin per day, with 'coin' and 'date' first.

    start and end are inclusive and optional, e.g. start="2018-01-01".
    'date' is always returned, even if not listed in columns.
    """
    columns = CLEAN_FIELDS if columns is None else list(columns)
    if "date" not in columns:
        columns = ["date", *columns]
    unknown = set(columns) - set(CLEAN_FIELDS)
    if unknown:
        raise ValueError(f"Unknown clean columns {sorted(unknown)}. Choose from {CLEAN_FIELDS}.")

    frames = []
    for coin in _as_list(coins):
        _check_unseen(coin, columns, UNSEEN_SAFE_CLEAN, unlock_unseen)
        folder = DESIGN if _group(coin) == "design" else UNSEEN
        path = folder / f"{coin}.parquet"
        if not path.exists():
            raise FileNotFoundError(f"No clean file for {coin} at {path}. Run the clean step first.")

        table = pd.read_parquet(path, columns=columns)
        if start is not None:
            table = table[table["date"] >= pd.Timestamp(start)]
        if end is not None:
            table = table[table["date"] <= pd.Timestamp(end)]
        table.insert(0, "coin", coin)
        frames.append(table)

    return pd.concat(frames, ignore_index=True).sort_values(["coin", "date"]).reset_index(drop=True)


def save_clean(table: pd.DataFrame, coin: str) -> None:
    """Write one coin's clean table to its folder, replacing any earlier version (reruns never duplicate)."""
    missing = set(CLEAN_FIELDS) - set(table.columns)
    if missing:
        raise ValueError(f"Clean table for {coin} is missing columns {sorted(missing)}.")
    if not table["date"].is_unique:
        raise ValueError(f"Clean table for {coin} has duplicate dates.")

    folder = DESIGN if _group(coin) == "design" else UNSEEN
    folder.mkdir(parents=True, exist_ok=True)
    table[CLEAN_FIELDS].sort_values("date").reset_index(drop=True).to_parquet(folder / f"{coin}.parquet", index=False)


# ------------------------------------------------------------------ derived

def load_derived(name: str, columns: list[str] | None = None) -> pd.DataFrame:
    """A processed table saved with save_derived, e.g. load_derived("regimes")."""
    path = DERIVED / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"No derived table {name!r} at {path}.")
    return pd.read_parquet(path, columns=columns)


def save_derived(table: pd.DataFrame, name: str) -> None:
    """Write a processed table, replacing any earlier version."""
    DERIVED.mkdir(parents=True, exist_ok=True)
    table.to_parquet(DERIVED / f"{name}.parquet", index=False)