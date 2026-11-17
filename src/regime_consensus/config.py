"""Fixed choices from NOTES.md. Every number in the spec lives here, and only here.

Add the signal parameters, fee and horizon to this file as you build each step,
so the spec and the code cannot drift apart.
"""

from datetime import date
from pathlib import Path

RUN_BUDGET = 20   # NOTES.md section 7

PROJECT_ROOT = Path(__file__).resolve().parents[2]   # config.py -> regime_consensus -> src -> project root
DATA_ROOT = PROJECT_ROOT / "data"
LOG_PATH = PROJECT_ROOT / "Documents" / "runs.csv"

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

# --- regime rules (NOTES.md section 3) ---
SLOW_LOOKBACK = 365   # days: 12-month convention (Goulding, Harvey and Mazzoleni, 2023)
FAST_LOOKBACK = 30    # days: 1-month convention
TIE_SIGN = -1         # a return of exactly zero counts as down: flat is not evidence of an uptrend
MIN_SPELL_DAYS = 20   # a spell counts towards the evidence rule only if it lasts at least this long
MIN_SPELLS = 5        # a state's result counts only with at least this many long spells

# --- Signal Rules
RSI_PERIOD = 14
RSI_UPPER = 70
RSI_MID = 50
RSI_LOWER = 30
ROC_LOOKBACKS = (5,10,20)
MACD_FAST, MACD_SLOW, MACD_SIGNAL = 12, 26, 9
BB_PERIOD = 20
BB_WIDTH = 2
Z_LOOKBACKS = (20, 50, 100)