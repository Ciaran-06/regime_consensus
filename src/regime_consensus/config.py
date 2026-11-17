"""Fixed choices from NOTES.md. Every number in the spec lives here, and only here.

Add the signal parameters, fee and horizon to this file as you build each step,
so the spec and the code cannot drift apart.
"""

from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]   # config.py -> regime_consensus -> src -> project root
DATA_ROOT = PROJECT_ROOT / "data"


# --- data source (NOTES.md section 5; provisional until the fund confirms its exchange) ---
EXCHANGE = "coinbase"

RAW = DATA_ROOT / "raw" / EXCHANGE      # put this line after EXCHANGE is defined
DESIGN = DATA_ROOT / "design"
UNSEEN = DATA_ROOT / "unseen"
FROZEN = DATA_ROOT / "frozen"
DERIVED = DATA_ROOT / "derived"         # labels, signals and other processed tables

# --- data split (NOTES.md section 5) ---
WARMUP_START = date(2017, 1, 1)   # only fills the 365-day lookbacks; no results measured here
DESIGN_START = date(2018, 1, 1)
DESIGN_END = date(2025, 12, 31)
FROZEN_START = date(2026, 1, 1)   # never downloaded or opened until the final test

# --- coins ---
DESIGN_COINS = ["BTC-USD", "ETH-USD"]
# Provisional list: the final one is fixed after checking each coin's first date (NOTES.md section 5)
UNSEEN_COINS = ["LTC-USD", "BCH-USD", "LINK-USD", "ETC-USD"]

