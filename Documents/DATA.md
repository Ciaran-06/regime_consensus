# DATA.md | regime_consensus | Data sources, layout, checks and known gaps

Last updated 17/11/26 (BCH gaps checked). After every download, rerun `scripts/00_download.py` and update this file.

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
| Downloaded | 16/11/26. **[TODO]** copy the exact time from `data/raw/coinbase/manifest.csv` |
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
└── frozen/                               empty until the final test; 2026 is downloaded only then
```

**Clean files:** one row per UTC day, columns `date`, `open`, `high`, `low`, `close`, `volume`. Duplicates removed, sorted by date, cut to 2017-01-01 to 2025-12-31. Nothing else has been changed.

- `date` is the UTC calendar day the candle covers, stored without a time zone.
- `volume` is in units of the coin, not dollars. **[TODO]** confirm against the API docs.

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

### Largest daily moves (BTC and ETH only)
- List the largest absolute close-to-close moves and check each against a known market event or an exchange glitch.
- *Reason:* a bad close feeds straight into the 365-day and 30-day trend signs. Coinbase has had exchange-specific glitches; ETH briefly crashed on its exchange in June 2017 (from memory), which is in the warm-up year.
- Allowed on BTC and ETH because the design period has already been seen. **Not run on the unseen coins** until claim 3.
- **[TODO]** results:

| Coin | Date | Move | Event or explanation | Action |
|---|---|---|---|---|
| | | | | |

### Zero-volume days (BTC and ETH only)
- A day with no trading has a stale price.
- **[TODO]** count per coin.

### Day boundaries
- **[TODO]** confirm every `time` value is exactly midnight UTC, so each candle covers one full UTC day.

---

## 5. Rules for using the data

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
- **Spot prices only.** Shorting needs perpetual futures, whose funding costs are not in this data.
- **The unseen coins are less liquid than BTC and ETH,** and their earlier years on Coinbase may have thinner trading.