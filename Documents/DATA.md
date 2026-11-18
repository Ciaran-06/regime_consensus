# DATA.md | regime_consensus | Data sources, layout, checks and known gaps

Last updated 18/11/26 (`volatility` and `correlations` derived tables added, run R03). After every download, rerun `scripts/00_download.py` and update this file.

Markers:
- **[TODO]** = a check still to run. Fill in the result and remove the marker.
- **[DRAFT]** = a proposed rule, to confirm before the data is used.

---

## 1. Source

| Item | Value |
|---|---|
| Exchange | Coinbase (public Exchange API, no account or key) |
| Endpoint | `GET https://api.exchange.coinbase.com/products/{product}/candles` |
| Granularity | `86400` seconds: one candle per UTC day |
| Fields returned | `time` (start of the day, Unix seconds), `low`, `high`, `open`, `close`, `volume` |
| Request size | 250 days per request (the API allows at most 300) |
| Date range requested | 2017-01-01 to 2025-12-31 |
| Downloaded | 2026-11-16 20:25 UTC (first block of `data/raw/coinbase/manifest.csv`; the 20:41 block is a rerun that downloaded nothing and matches it exactly) |
| Script | `scripts/00_download.py`, settings in `src/regime_consensus/config.py` |

- **Provisional source.** Chosen because it matches V2's data. To be revisited once the fund confirms its exchange (NOTES.md, Open questions).
- **The API warns its historical data may be incomplete:** no candle is published for a day with no trades.
- **2026 was never requested.** The script refuses any request after 2025-12-31 and discards any later candle the API returns. No candle was discarded on 16/11/26.

---

## 2. Layout

```
data/                                     not in git
├── raw/coinbase/
│   ├── <coin>/<from>_<to>.json           API responses, saved unchanged, never edited
│   └── manifest.csv                      one block per download: time, range, coverage
├── design/<coin>.parquet                 BTC-USD, ETH-USD
├── unseen/<coin>.parquet                 LTC-USD, BCH-USD (deciding); ETC-USD, LINK-USD (secondary)
├── derived/<name>.parquet                processed tables (labels, signals, volatility, correlations)
└── frozen/                               empty until the final test; 2026 is downloaded only then
```

### File structure

**Raw** `data/raw/coinbase/<coin>/<from>_<to>.json`
- A JSON list of candles, newest first, exactly as the API returned them.
- Each candle: `[time, low, high, open, close, volume]`. `time` is Unix seconds (an integer); the rest are numbers.
- Load with `load_raw(coins, columns)` from `regime_consensus.io`.

**Clean** `data/design/<coin>.parquet` and `data/unseen/<coin>.parquet`
- One row per UTC day. Key: `date` (unique within a file). Sorted by `date`, oldest first.
- Built from raw by removing duplicates, sorting and cutting to 2017-01-01 to 2025-12-31. Nothing else has been changed.

| Column | Type | Meaning |
|---|---|---|
| `date` | datetime, no time zone | the UTC day the candle covers |
| `open` | float | first trade of the day, USD |
| `high` | float | highest trade, USD |
| `low` | float | lowest trade, USD |
| `close` | float | last trade of the day, USD |
| `volume` | float | amount traded, in units of the coin. **[TODO]** confirm against the API docs |

- Load with `load_clean(coins, columns, start, end)` from `regime_consensus.io`, which adds a `coin` column first. Unseen coins return `date` and `volume` only.

**Derived** `data/derived/<name>.parquet`
- Processed tables (regime labels, signals, volatility labels, correlations). Each is documented here when it is first created.
- Load with `load_derived(name, columns)` from `regime_consensus.io`.

**`regimes`** `data/derived/regimes.parquet` (run R01, 17/11/26)
- Built by `scripts/01_regimes.py` with `label_regimes` from `src/regime_consensus/regime_modeling.py`.
- BTC and ETH, 2018-01-01 to 2025-12-31. One row per coin per day: 2,922 rows per coin, 5,844 in total. Key: (`coin`, `date`).
- Labels are computed on 2017–2025 closes, then cut to 2018 onwards, so 2017 only fills the 365-day lookbacks.

| Column | Type | Meaning |
|---|---|---|
| `coin` | text | e.g. `BTC-USD` |
| `date` | datetime, no time zone | the UTC day |
| `slow` | float, +1 or −1 | sign of the return over the past 365 days |
| `fast` | float, +1 or −1 | sign of the return over the past 30 days |
| `state` | text | `BULL`, `CORRECTION`, `BEAR` or `REBOUND` |

- A return of exactly zero would count as −1 (NOTES.md section 3). Checked 17/11/26: **0 ties** for both coins at both lookbacks, so the rule never applied.

**`signals`** `data/derived/signals.parquet` (run R02, 18/11/26)
- Built by `scripts/02_signals.py` with `build_signals` from `src/regime_consensus/signals.py` and `family_vote` from `src/regime_consensus/agreement.py`.
- BTC and ETH, 2018-01-01 to 2025-12-31. One row per coin per day: 2,922 rows per coin, 5,844 in total. Key: (`coin`, `date`).
- Signals are computed on 2017–2025 closes, then cut to 2018 onwards. The longest lookback is 100 days (z-score), so 2017 covers every warm-up.
- Definitions of every signal are in NOTES.md section 6.

| Column | Type | Meaning |
|---|---|---|
| `coin` | text | e.g. `BTC-USD` |
| `date` | datetime, no time zone | the UTC day |
| `<signal>_score` | float | the signal's strength and direction; positive means "expect the price to rise" |
| `<signal>_vote` | float: +1, −1 or NaN | the signal's direction, or NaN for no reading |
| `momentum_vote` | float: +1, −1 or NaN | majority of the votes of the signals in `MOMENTUM_CANDIDATES`, NaN if no majority |
| `reversion_vote` | float: +1, −1 or NaN | majority of the votes of the signals in `REVERSION_SIGNALS`, NaN if no majority |

- `<signal>` is one of `rsi_50`, `rate_of_change`, `macd` (momentum) and `rsi_extreme`, `bollinger`, `z_score` (mean reversion), in that column order.
- Checked 18/11/26: **0 missing scores** for every signal in 2018–2025, so no flat-RSI days.
- **The family votes in the R02 table use all three signals per family.** The correlation pre-check (R03) dropped `rate_of_change` and `bollinger`, so the table is rebuilt in R04 with family votes from `rsi_50` and `macd` (momentum) and `rsi_extreme` and `z_score` (mean reversion); with two signals the majority rule means both agree. All six scores and votes stay in the table, so the dropped signals can still be reported. Update this entry after R04.

**`volatility`** `data/derived/volatility.parquet` (run R03, 18/11/26)
- Built by `scripts/03_correlation.py` with `label_volatility` from `src/regime_consensus/regime_modeling.py`. Rule in NOTES.md section 3.
- BTC and ETH, 2018-01-01 to 2025-12-31. One row per coin per day: 2,922 rows per coin, 5,844 in total. Key: (`coin`, `date`).
- Labels are computed on 2017–2025 closes, then cut to 2018 onwards.

| Column | Type | Meaning |
|---|---|---|
| `coin` | text | e.g. `BTC-USD` |
| `date` | datetime, no time zone | the UTC day |
| `volatility` | text or NaN | `HIGH` (turbulent) if 30-day realised volatility of daily log returns is above its median over the previous 365 days, `LOW` (calm) otherwise; NaN before enough history |

- **The first label is on 2018-01-31.** The 365-day median of 30-day volatility needs 395 days of closes from 2017-01-01, so 2018-01-01 to 2018-01-30 have no label (30 days per coin).
- Checked 18/11/26: BTC 1,625 calm, 1,267 turbulent, 30 unlabelled; ETH 1,568 calm, 1,324 turbulent, 30 unlabelled.
- The median uses the 365 days **before** day $t$ (shifted by one day), so day $t$'s volatility is never compared with itself.

**`correlations`** `data/derived/correlations.parquet` (run R03, 18/11/26)
- Built by `scripts/03_correlation.py`. Spearman rank correlations of the six signal scores, per coin, on all days, calm days and turbulent days (the `volatility` table above).
- 216 rows: 2 coins × 3 periods × 36 ordered signal pairs. Key: (`coin`, `period`, `signal_a`, `signal_b`).
- Long format: each pair appears twice (a, b and b, a), and each signal with itself has `rho` = 1.

| Column | Type | Meaning |
|---|---|---|
| `coin` | text | e.g. `BTC-USD` |
| `period` | text | `all`, `calm` or `turbulent` |
| `signal_a` | text | one of the six signal names |
| `signal_b` | text | one of the six signal names |
| `rho` | float | Spearman rank correlation between the two signals' daily scores in that period |

- Only the `all` rows decide which signals are kept (NOTES.md section 4); `calm` and `turbulent` are reported only.
- Days in each period: all 2,922 per coin; calm and turbulent as in the `volatility` table.

---

## 3. Coverage (16/11/26)

| Group | Coin | Rows | First date | Last date | Missing days | Bad rows |
|---|---|---|---|---|---|---|
| design | BTC-USD | 3,287 | 2017-01-01 | 2025-12-31 | 0 | 0 |
| design | ETH-USD | 3,287 | 2017-01-01 | 2025-12-31 | 0 | 0 |
| unseen | LTC-USD | 3,287 | 2017-01-01 | 2025-12-31 | 0 | 0 |
| unseen | BCH-USD | 2,930 | 2017-12-20 | 2025-12-31 | 4 | 0 |
| unseen | LINK-USD | 2,380 | 2019-06-27 | 2025-12-31 | 0 | 0 |
| unseen | ETC-USD | 2,703 | 2018-08-08 | 2025-12-31 | 0 | 0 |

- 3,287 rows = every day from 2017-01-01 to 2025-12-31 (nine years plus two leap days), so BTC, ETH and LTC are complete.
- **Missing days** = days between the coin's first date and 2025-12-31 with no candle.
- **Bad rows** = any price at or below zero, high below low, or close outside the high–low range.
- The unseen coins' coverage uses dates and these sanity checks only. **No unseen-coin prices have been looked at.**

---

## 4. Checks

### BCH missing days (checked 17/11/26, dates only)
- **2018-11-16, 2018-11-17, 2018-11-18, 2018-11-19.** Found by comparing a full daily calendar with BCH's dates. This matches the download log: the request for 2018-05-16 to 2019-01-20 returned 246 of 250 days.
- **Cause:** Coinbase paused BCH trading around the Bitcoin Cash split of 15 November 2018 (from memory; confirm against Coinbase's announcement before citing).
- **Action:** BCH is treated as a new coin from 2018-11-20. No BCH data before that date is used, and its regime labels start on 2019-11-20, after a fresh 365-day warm-up. Reason and cost are in NOTES.md section 5.

### Largest daily moves (BTC and ETH only, checked 17/11/26)
- *Reason:* a bad close feeds straight into the 365-day and 30-day trend signs.
- *Method* (`Notebooks/big_moves.py`): the 10 largest absolute close-to-close returns per coin, 2017–2025 (warm-up included, since it feeds the trend labels). Each is tested two ways:
  - **Co-move:** the other coin moved the same way by at least a third as much. Real market events move both coins; a glitch on one feed usually doesn't.
  - **Reversal:** the next day went the other way by at least half as much. A bad close shows up as a big move followed by a big move back.
  - **Suspect** = no co-move **and** reversed.
- Allowed on BTC and ETH because the design period has already been seen. **Not run on the unseen coins** until claim 3.
- **Result: 0 suspect days out of 20.** No sign of a glitched close.
- Event names below are from memory. Verify any before citing it.

| Coin | Date | Move | Other coin | Next day | Explanation | Action |
|---|---|---|---|---|---|---|
| BTC | 2017-07-17 | +16.9% | +22.6% | +3.3% | Market-wide rally | None |
| BTC | 2017-07-20 | +27.2% | +16.1% | −7.5% | Market-wide rally (Bitcoin SegWit upgrade news) | None |
| BTC | 2017-09-14 | −15.7% | −18.8% | +15.1% | Market-wide fall (China exchange crackdown news), rebound next day | None |
| BTC | 2017-12-06 | +20.2% | −5.4% | +23.4% | BTC-only: December 2017 rally | None |
| BTC | 2017-12-07 | +23.4% | +0.2% | −5.9% | BTC-only: December 2017 rally | None |
| BTC | 2019-04-02 | +18.5% | +16.8% | +1.5% | Market-wide rally | None |
| BTC | 2019-10-25 | +16.6% | +13.1% | +6.8% | Market-wide rally | None |
| BTC | 2020-03-12 | −38.8% | −43.3% | +16.1% | COVID crash | None |
| BTC | 2020-03-13 | +16.1% | +22.9% | −8.4% | Rebound after the COVID crash | None |
| BTC | 2021-02-08 | +19.5% | +8.5% | +0.1% | Market-wide rally (Tesla's Bitcoin purchase announced) | None |
| ETH | 2017-03-15 | +24.3% | +1.2% | +28.9% | ETH-only: March 2017 rally | None |
| ETH | 2017-03-16 | +28.9% | −7.0% | −2.9% | ETH-only: March 2017 rally | None |
| ETH | 2017-03-18 | −24.6% | −9.3% | +28.4% | Fall during the March 2017 rally, rebound next day | None |
| ETH | 2017-03-19 | +28.4% | +5.1% | −2.1% | ETH-only: March 2017 rally | None |
| ETH | 2017-05-19 | +30.1% | +4.1% | −1.2% | ETH-only: May 2017 rally | None |
| ETH | 2017-12-12 | +32.6% | +5.0% | +3.7% | ETH-only: December 2017 rally | None |
| ETH | 2020-03-12 | −43.3% | −38.8% | +22.9% | COVID crash, rebound next day | None |
| ETH | 2021-01-03 | +26.5% | +2.7% | +6.3% | ETH-only: rally towards $1,000 | None |
| ETH | 2021-05-19 | −27.6% | −14.3% | +13.6% | Market-wide crash (May 2021) | None |
| ETH | 2021-05-24 | +26.3% | +11.9% | +2.1% | Rebound after the May 2021 crash | None |

- **Eight moves were made by one coin only.** All are known rallies, and none reversed the way a bad close would. Six of the eight are in 2017, the warm-up year, when trading on Coinbase was much thinner.
- **The June 2017 ETH flash crash on Coinbase does not appear.** It happened within a day, so the daily close was not affected.

### Zero-volume days (all six coins)
- A day with no trading has a stale price.
- Checked 17/11/26: no zero-volume days for any of the six coins (date and volume columns only).

### Day boundaries
- Checked 17/11/26: every candle for all six coins starts at exactly 00:00 UTC (every time divides by 86,400).

---

## 5. Rules for using the data

- **No data in use has a gap.** BCH's four missing days fall before 2018-11-20, so the fork rule below already removes them. The three gap rules that follow are safeguards for any later download, such as the frozen 2026 data.
- **[DRAFT]** **Gaps are never filled in.** No price is copied forward or interpolated.
- **[DRAFT]** **Any 5-day forward window that contains a missing day is dropped,** for every coin.
- **[DRAFT]** **Any trend lookback that contains a missing day** is computed from the closes on either side of the gap; no regime label is assigned on a missing day itself.
- **BCH fork rule:** BCH data before 2018-11-20 is never used. Its warm-up runs from 2018-11-20, so its labels start on 2019-11-20 (NOTES.md section 5).
- **Warm-up:** 2017 is used only to fill the 365-day lookbacks. No result is measured on it.
- **Frozen data:** nothing after 2025-12-31 is downloaded until the final test.

---

## 6. Lookahead warnings

- A regime label on day $t$ uses closes up to and including day $t$ only.
- A signal on day $t$ is traded at the earliest on day $t+1$. The close that produced the signal is never the fill price (BACKTESTING.md rule 8).
- The 5-day forward return for day $t$ uses the close on day $t$ and day $t+5$. It is a target, never a feature.
- Any threshold (for example the volatility median) uses past data only, never the whole sample.

---

## 7. Known limitations

- **One exchange.** Coinbase prices can differ from other venues, especially during outages and flash crashes.
- **Daily closes at midnight UTC are a convention.** Crypto trades continuously, so another cut-off would give slightly different returns.
- **Spot prices only.** The strategy is long or flat (NOTES.md), so shorting and perpetual-futures funding costs are not needed.
- **The unseen coins are less liquid than BTC and ETH,** and their earlier years on Coinbase may have thinner trading.
- **2017 prices are thin and volatile,** especially ETH's. 2017 is warm-up only, but it feeds the 365-day trend sign through 2018, so early-2018 labels rest partly on those prices.