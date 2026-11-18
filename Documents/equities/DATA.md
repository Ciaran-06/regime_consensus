# DATA.md (equities study) | regime_consensus | Last updated 18/11/26 (source facts only; no data loaded)

**Status:** No equity data has been copied into the project. This file records facts about the sources gathered on 18/11/26. None of them involved looking at returns. The crypto study's data file is `Documents/crypto/DATA.md`.

---

## 1. Sources

| Source | Use | Status |
|---|---|---|
| CRSP via WRDS (QuantSoc subscription) | Stock returns, delisting returns, S&P 500 constituent history | Requested 18/11/26 (primary) |
| Compustat historical GICS via WRDS | Point-in-time sector classification | Requested 18/11/26 (primary) |
| IVolatility REST API, Builder plan | Implied volatility (IVX), sector ETF prices, stock prices (fallback), dividends (fallback) | Available. Existing downloads in `D:\DATA\ivol_data`, built for the earningVol project |
| hanshof/sp500_constituents (GitHub) | S&P 500 membership history (fallback) | In `D:\DATA\sp500_former_members.csv` |

- **IVolatility plan:** 50 years of history allowed. 20,000 end-of-day calls a month, **resetting on the 13th**. About 18,300 left on 18/11/26.

---

## 2. IVolatility facts (checked with IVolatility's assistant, 18/11/26)

### Coverage start dates
| Series | First date | Note |
|---|---|---|
| Single-stock prices | 1995-01-03 | Data floor for stocks (IBM, GE, XOM, JNJ) |
| ETF prices | 1999-01-04 | Data floor for ETFs, even those listed earlier (SPY 1993, DIA and MDY earlier) |
| QQQ / IWM / EFA / TLT / GLD prices | 1999-03-10 / 2000-05-26 / 2002-07-01 / 2003-05-16 / 2004-11-18 | |
| Sector SPDR prices (XLB, XLE, XLF, XLI, XLK, XLU, XLV, XLY) | 1999-01-04 | XLP from 1998-12-22 |
| Single-stock IVX | 1999-05-19 | Floor for stock implied volatility |
| SPY IVX | 2005-01-10 | |
| Sector SPDR IVX, first date | XLB, XLI 1999-05-19; XLY 1999-08-17; XLU 2000-03-29; XLF, XLK 2000-03-20; XLV 2000-04-06; XLE 2000-04-07; XLP 2000-04-12 | |

- **Unreliable early sector IVX:** XLY reports 30-day IV of 150–228% from 1999-08-17 to 1999-10-29 and has gaps to 2000-03-02; XLI is sparse (14 days) in May–June 1999, then missing until 2000-04-17. **[DRAFT] rule:** sector IVX before 2000-04-17 is not used.
- IVX values are fractions (0.257 = 25.7%).

### Timestamps
- `close` in stock prices is the **official 4pm ET close**.
- IVX is built from the **4pm closing option quotes** (IVolatility rebuilt AAPL's 30- and 60-day values from the closing chain within 0.03–0.07 vol points; the 3:45pm snapshot chain was 0.15–0.25 points off). The IVX row's `price` equals the official close.
- *Consequence:* a signal computed from the close cannot be traded at that same close. Trades happen on day $t+1$ at the earliest (BACKTESTING.md rule 8).
- Closing option quotes are often wide. A separate 3:45pm option dataset (`stock-opts-by-param-1545`) exists if tradable option quotes are ever needed.

### Prices and dividends
- `open`, `high`, `low`, `close` are **split-adjusted only**; `unadjusted_close` is the traded price. Dividends are **not** in the prices.
- `/equities/corp-actions` returns, per symbol, the full history (no date filter) of:
  - `Regular dividend` (`Date` = ex-date, `amount` per share, `frequency`);
  - `Cash Dividend` (special dividends: `amount` and a price-adjustment `factor`);
  - `Split` (`factor` = ratio, e.g. 4.0 for 4-for-1);
  - `Trading Halt`, `Acquisition`, `First Option`, `Start trading`.
- **Traps:** dividend amounts are as paid, not restated for later splits; the same dividend can appear twice on one date (AAPL 2020-08-07: 0.82 and 0.205, before and after its split restatement). Deduplicate by date. Coverage is US stocks with listed options. **To confirm:** whether ETFs are covered.
- **Total return, if IVolatility prices are used:** on ex-date $t$, convert the nominal dividend $D_t$ to the adjusted price basis and add it back:

$$
D^{\text{adj}}_t = D_t \times \frac{C^{\text{adj}}_t}{C^{\text{raw}}_t},
\qquad
R_t = \frac{C^{\text{adj}}_t + D^{\text{adj}}_t}{C^{\text{adj}}_{t-1}} - 1
$$

### Reference data
- `/equities/underlying-info` returns listing metadata (CUSIP, ISIN, FIGI, StockID, option start date, dividend convention as of the requested date). **It has no sector field.** It can return duplicate rows, and one symbol can map to several listings (for example a Montreal-listed AAPL option series). Deduplicate and filter by `StockID`.
- `/equities/trading-calendar` gives US trading days and holidays.

### Known gaps from the earningVol project's checks
- 18 former S&P 500 members have no price data at all (AT, H, VRTS, MMI, WB, AM, PD, ADCT, ASO, CCU, DYN, EQ, GP, LU, TE, WFG, CR, LB).
- Former members' prices were downloaded only for one year before joining to one year after leaving. Current members have full history, including years before they joined, so an "in the index on this date" flag is required.
- `hv` covers current members and ETFs only (survivorship-biased): use computed realised volatility for stocks.

---

## 3. Rules [DECIDE]

To be written with the data split (NOTES.md section 5), before any equity data is copied into the project's `data/` folder.