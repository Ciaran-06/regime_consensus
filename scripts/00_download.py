"""Download daily candles from Coinbase's public Exchange API. No account or API key is needed.

Run from the project root:
    uv run python scripts/00_download.py            # everything in config
    uv run python scripts/00_download.py --test     # one small request, to check the API works

What it does
    1. Requests daily candles in chunks (the API allows at most 300 candles per request).
    2. Saves each response untouched in data/raw/coinbase/<coin>/<from>_<to>.json.
    3. Builds one clean file per coin: data/design/<coin>.parquet or data/unseen/<coin>.parquet.
    4. Prints a coverage report and appends it to data/raw/coinbase/manifest.csv.

Safety
    The script never requests a date after config.DESIGN_END, so the frozen 2026 data
    is never downloaded. Rerunning is safe: chunks already on disk are skipped.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from regime_consensus import config

API_URL = "https://api.exchange.coinbase.com/products/{product}/candles"
GRANULARITY = 86400          # seconds in a day: one candle per UTC day
CHUNK_DAYS = 250             # under the API's limit of 300 candles per request
PAUSE_SECONDS = 0.5          # be polite: the docs say not to poll this endpoint frequently
MAX_TRIES = 4

DATA_ROOT = Path(__file__).resolve().parents[1] / "data"
RAW_DIR = DATA_ROOT / "raw" / config.EXCHANGE
CANDLE_FIELDS = ["time", "low", "high", "open", "close", "volume"]  # order the API returns


def date_chunks(start: date, end: date) -> list[tuple[date, date]]:
    """Split [start, end] into consecutive chunks of at most CHUNK_DAYS days, both ends included."""
    chunks = []
    chunk_start = start
    while chunk_start <= end:
        chunk_end = min(chunk_start + timedelta(days=CHUNK_DAYS - 1), end)
        chunks.append((chunk_start, chunk_end))
        chunk_start = chunk_end + timedelta(days=1)
    return chunks


def fetch_chunk(product: str, chunk_start: date, chunk_end: date) -> list[list[float]]:
    """One API request. Returns the raw list of candles (possibly empty)."""
    if chunk_end > config.DESIGN_END:
        raise ValueError(f"Refusing to request {chunk_end}: it is after DESIGN_END (frozen data).")

    query = urllib.parse.urlencode(
        {
            "granularity": GRANULARITY,
            "start": f"{chunk_start.isoformat()}T00:00:00Z",
            "end": f"{chunk_end.isoformat()}T23:59:59Z",
        }
    )
    request = urllib.request.Request(
        API_URL.format(product=product) + "?" + query,
        headers={"User-Agent": "regime_consensus research script", "Accept": "application/json"},
    )

    for attempt in range(1, MAX_TRIES + 1):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            if error.code == 404:
                raise ValueError(f"{product} was not found on the exchange.") from error
            if error.code in (429, 500, 502, 503, 504) and attempt < MAX_TRIES:
                time.sleep(2**attempt)  # wait 2, 4, 8 seconds, then try again
                continue
            raise
        except urllib.error.URLError:
            if attempt < MAX_TRIES:
                time.sleep(2**attempt)
                continue
            raise
    return []


def drop_frozen(candles: list[list[float]]) -> list[list[float]]:
    """Guard: the API can return candles outside the requested range. Never keep one after DESIGN_END."""
    last_allowed = datetime.combine(config.DESIGN_END, datetime.max.time(), tzinfo=timezone.utc).timestamp()
    kept = [c for c in candles if c[0] <= last_allowed]
    if len(kept) < len(candles):
        print(f"    dropped {len(candles) - len(kept)} candle(s) dated after DESIGN_END (not saved)")
    return kept


def download_raw(product: str) -> None:
    """Fetch every chunk for one coin and save each response as returned."""
    coin_dir = RAW_DIR / product
    coin_dir.mkdir(parents=True, exist_ok=True)

    for chunk_start, chunk_end in date_chunks(config.WARMUP_START, config.DESIGN_END):
        out_file = coin_dir / f"{chunk_start}_{chunk_end}.json"
        if out_file.exists():
            continue  # already downloaded
        candles = drop_frozen(fetch_chunk(product, chunk_start, chunk_end))
        out_file.write_text(json.dumps(candles))
        print(f"    {chunk_start} to {chunk_end}: {len(candles)} candles")
        time.sleep(PAUSE_SECONDS)


def build_clean(product: str) -> pd.DataFrame:
    """Combine the raw chunks into one table: date, open, high, low, close, volume (one row per UTC day)."""
    rows: list[list[float]] = []
    for raw_file in sorted((RAW_DIR / product).glob("*.json")):
        rows.extend(json.loads(raw_file.read_text()))

    table = pd.DataFrame(rows, columns=CANDLE_FIELDS)
    if table.empty:
        return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])

    table["date"] = pd.to_datetime(table["time"], unit="s", utc=True).dt.tz_localize(None).dt.normalize()
    table = table.drop_duplicates(subset="date").sort_values("date")

    in_range = (table["date"] >= pd.Timestamp(config.WARMUP_START)) & (table["date"] <= pd.Timestamp(config.DESIGN_END))
    table = table.loc[in_range, ["date", "open", "high", "low", "close", "volume"]].reset_index(drop=True)
    return table


def coverage(product: str, table: pd.DataFrame) -> dict:
    """Coverage and sanity checks. Uses dates and basic price sanity only, never returns."""
    if table.empty:
        return {"product": product, "rows": 0, "first_date": None, "last_date": None,
                "missing_days": None, "bad_rows": None}

    first, last = table["date"].min(), table["date"].max()
    expected_days = pd.date_range(first, pd.Timestamp(config.DESIGN_END), freq="D")
    missing = expected_days.difference(pd.DatetimeIndex(table["date"]))
    bad = (
        (table[["open", "high", "low", "close"]] <= 0).any(axis=1)
        | (table["high"] < table["low"])
        | (table["close"] > table["high"])
        | (table["close"] < table["low"])
    )
    return {
        "product": product,
        "rows": len(table),
        "first_date": first.date(),
        "last_date": last.date(),
        "missing_days": len(missing),
        "bad_rows": int(bad.sum()),
    }


def run_test() -> None:
    """One small request, to confirm the API answers without a key."""
    candles = fetch_chunk("BTC-USD", date(2024, 1, 1), date(2024, 1, 5))
    print(f"Received {len(candles)} candles for BTC-USD, 2024-01-01 to 2024-01-05 (expected 5).")
    for candle in sorted(candles):
        day = datetime.fromtimestamp(candle[0], tz=timezone.utc).date()
        print(f"  {day}  fields: {dict(zip(CANDLE_FIELDS[1:], candle[1:]))}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download daily candles for regime_consensus.")
    parser.add_argument("--test", action="store_true", help="make one small request and exit")
    args = parser.parse_args()

    if config.DESIGN_END >= config.FROZEN_START:
        raise SystemExit("config error: DESIGN_END must be before FROZEN_START.")
    if args.test:
        run_test()
        return

    groups = [("design", config.DESIGN_COINS), ("unseen", config.UNSEEN_COINS)]
    reports = []
    for folder, coins in groups:
        (DATA_ROOT / folder).mkdir(parents=True, exist_ok=True)
        for product in coins:
            print(f"{product} ({folder})")
            try:
                download_raw(product)
            except ValueError as problem:
                print(f"    skipped: {problem}")
                continue
            table = build_clean(product)
            table.to_parquet(DATA_ROOT / folder / f"{product}.parquet", index=False)
            reports.append({"group": folder, **coverage(product, table)})

    summary = pd.DataFrame(reports)
    count_columns = ["rows", "missing_days", "bad_rows"]
    summary[count_columns] = summary[count_columns].astype("Int64")  # whole numbers, blank where a coin has no data
    print("\nCoverage (dates and sanity checks only):")
    print(summary.to_string(index=False))

    summary.insert(0, "downloaded_at_utc", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"))
    summary.insert(1, "requested_from", config.WARMUP_START)
    summary.insert(2, "requested_to", config.DESIGN_END)
    manifest = RAW_DIR / "manifest.csv"
    summary.to_csv(manifest, mode="a", header=not manifest.exists(), index=False)
    print(f"\nAppended to {manifest}")


if __name__ == "__main__":
    main()