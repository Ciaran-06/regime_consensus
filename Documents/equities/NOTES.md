# NOTES.md (equities study) | regime_consensus | Last updated 18/11/26 (study opened)

**Status:** Opened on 18/11/26. Section 0 (the pivot) is decided. Every other section is a skeleton: items marked **[DECIDE]** are open, items marked **[DRAFT]** are proposals carried over from the crypto study that must be confirmed or changed, each with a date and a reason, before any equity data enters the project. No equity data has been loaded into the project and no forward return has been computed.

The rules every test follows are in `Documents/BACKTESTING.md`. The crypto study's spec is `Documents/crypto/NOTES.md`.

**Markers:** **[DECIDE]** = open decision. **[DRAFT]** = proposed, not yet confirmed. An item with neither is decided.

---

## 0. Pivot to equities (decided 18/11/26)

### The decision
- **Equities become the primary study.** The crypto study (`Documents/crypto/NOTES.md`) becomes its out-of-asset-class replication, run afterwards from the git tag `crypto-prechecks-v1`.
- **Design, at the level decided so far:**
  - **Claim 1 (agreement)** is tested on single US stocks, for statistical breadth.
  - **Claims 2 and 3 (regime dependence and switching)** use the trend regime of each stock's **sector**, measured on the sector SPDR ETF. Signals come from the stock; the regime comes from its sector. The traded instruments in claim 3 are the stocks.

### Reasons
1. **The sources were written for equities.** Goulding, Harvey and Mazzoleni (2023) define the trend states on equity markets; Nagel (2012) and Campbell, Grossman and Wang (1993) study stocks. The crypto spec had to assume these carried over.
2. **An unseen design period.** The crypto design period had been seen through 38 V1/V2 backtests. No equity momentum, reversal or regime returns have been examined (see "What has been seen" below).
3. **More independent regime evidence.** Sector ETF data from 1999 and stock data from 1995 cover the 2000–02, 2008, 2020 and 2022 bear markets, and sectors move out of step with each other (for example, energy's 2014–16 bear market while the index rose), so regime spells are more numerous and less dependent than in two coins.
4. **A non-price signal exists.** Implied volatility (IVX) comes from the options market, so its errors need not match those of price-based signals (Dietterich's diversity condition). The crypto study's attempt to find a non-price reversal signal closed without a supported candidate (`Documents/crypto/NOTES.md`, section 13).
5. **Why sectors carry the regime:** much of stock momentum comes from industry momentum (Moskowitz and Grinblatt, 1999, *Journal of Finance*), and short-term reversal is strongest once industry moves are removed (Da, Liu and Schaumburg, 2014, *Management Science*). Both cited from memory; **check before citing**. A sector's trend is also less contaminated by company news than a single stock's.
6. **The fund trades whatever universe the strategy uses,** as understood on 18/11/26. To confirm in writing with the head of QuantSoc (section 10).

### What has been seen in the equity data (disclosed in full)
- The IVolatility dataset in `D:\DATA` was built for an earlier project (earnings straddles, repo earningVol). In that project the following were examined: earnings-day price moves and option prices around earnings for S&P 500 names, 2004–2026, including a holdout from 2024-01-01; the NVDA option chain; data-quality checks on prices, IVX and calendars.
- **Not examined:** returns of any momentum, reversal or trend signal; returns by sector or by trend state; any ETF return series. The design period is therefore unseen **for this question**.
- Data facts gathered on 18/11/26 (coverage start dates, timestamps, dividend fields) involved no returns. They are recorded in `Documents/equities/DATA.md`.

### Rigour standard (decided 18/11/26, applies to every decision in this study)
For every decision, the most rigorous option is chosen even when it costs more work. "Rigorous" means: the best available data, the fewest free choices (each setting has a source or a stated default), and every rule fixed and dated before the result it affects. Adding signals or settings is not in itself more rigorous; each added choice must justify itself under this standard.

### Data sources (decided 18/11/26)
- **Primary:** CRSP (daily stock file, delisting returns, S&P 500 constituent history) and Compustat historical GICS, through QuantSoc's WRDS subscription (requested 18/11/26); IVolatility for implied volatility and sector ETF prices, joined to CRSP by CUSIP.
- **Fallback, fixed now so the choice cannot follow any result:** if WRDS access has not arrived by **2026-12-18**, the study uses IVolatility for stock prices, `corp-actions` for dividends, the existing S&P 500 membership history, and return-based sector assignment. The limitations (stocks with no price history, no delisting returns) are then stated in section 8.

### Sector assignment (decided 18/11/26)
- **Primary:** point-in-time GICS from Compustat.
  - *Reason:* Bhojraj, Lee and Oler (2003, *Journal of Accounting Research* 41(5)) find GICS significantly better than SIC, NAICS and Fama–French at explaining stock return comovement, which is the property a sector regime relies on.
- **Robustness check 1:** each stock assigned to the sector ETF its daily returns correlate with most over the previous 252 trading days, reassigned monthly. Point-in-time by construction. **[DRAFT]** the 252-day window and monthly reassignment.
- **Robustness check 2:** today's GICS applied to all dates, labelled as having lookahead (for example, Communication Services did not exist before 2018).
- **SIC codes are not used:** weaker on comovement (Bhojraj, Lee and Oler, 2003), needing a hand-made mapping to the SPDR sectors, and hard to reconstruct point-in-time.
- **If the fallback applies:** return-based assignment becomes primary.

### Run budget (decided 18/11/26)
- **A new budget of 20 runs** for the equities study, logged in the shared `Documents/runs.csv` under `study = equities`.
- *Reason:* the budget caps how often one design period is looked at. No equity return has been examined, and no crypto run computed a forward return, so the crypto runs do not use up the equity test. Both studies' runs stay in one log so the full history is visible.

---

## 1. Hypothesis [DRAFT]

Carried over from the crypto study and restated for this design. Wording, sources and weak points to be confirmed.

1. **Agreement.** When several weak signals on a stock point the same way, the stock's subsequent returns are better than when acting on any one of those signals alone.
   - *Sources:* Timmermann (2006); Dietterich (2000), as in the crypto study.
2. **Regime dependence.** Which signal family works better on a stock depends on the trend regime of its sector.
   - *Mechanisms:* attention for continuation (source to be re-read for equities: the crypto study used Liu and Tsyvinski, 2021, which is crypto-specific) **[DECIDE]**; liquidity provision for reversal (Nagel, 2012).
3. **Switching.** A portfolio that follows, for each stock, the family its sector's regime predicts beats holding either family all the time, after costs.
   - **[DECIDE]** long only, or long and short (Alpaca allows shorting stocks; the fund's rules on shorting to be confirmed).

---

## 2. Background

- The crypto study's history (V1 and V2 backtests, runs R01–R06) is in `Documents/crypto/NOTES.md`. None of it is evidence for or against this study.
- The R03 and R06 findings that matter here, as warnings, not results: price-based signals within a family were correlated at about 0.55–0.6, and the two families were near mirror images (RSI relative to 50 and z-score at $\rho \approx -0.98$). The same may happen with equities; the pre-check in section 4 is designed to catch it.

---

## 3. Regime definitions [DECIDE]

- **[DRAFT]** Slow and fast trend from 12-month and 1-month returns (Goulding, Harvey and Mazzoleni, 2023), in trading days: 252 and 21.
- **[DRAFT]** The four states and the predicted family table (Bull: momentum; Correction: mean reversion; Bear: momentum; Rebound: no prediction).
- **[DECIDE]** The sector ETFs used: the nine original sector SPDRs (XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY) from 1998–99; how XLRE (2015) and XLC (2018) and their reclassified stocks are handled.
- **[DECIDE]** Minimum evidence per state (the crypto rule was 5 spells of at least 20 days), and whether spells are counted per sector.
- **[DECIDE]** The volatility rule (crypto: 30-day realised volatility against its 365-day median), or an implied-volatility version.

---

## 4. Kill tests [DECIDE]

- **[DRAFT]** One confirmatory run per claim; all other runs diagnostic.
- **[DRAFT]** The correlation pre-check (rank correlations, near-copies above 0.7, fixed priority order).
- **[DRAFT]** Claim 1 details A, C and D from the crypto study (agreement must beat every member; fallback to equal-weighted signed-rank averages; date-averaged differences with Newey–West standard errors). With hundreds of stocks, the averaging is across all stocks on each date.
- **[DECIDE]** Earnings: whether days with an earnings announcement inside the forward window are excluded from claim 1, and how claim 3 handles earnings (hold through, or go flat using dates known in advance).
- **[DECIDE]** Claim 3 benchmarks, including the same rule driven by the market (SPY) regime, to test whether sector regimes add anything.
- **[DECIDE]** The decision table.

---

## 5. Data split [DECIDE]

- **[DECIDE]** Design period, warm-up, frozen test period and held-out set. 2026 data already exists on disk in `D:\DATA`, so the frozen period must be fixed before any equity data is copied into the project.
- **[DECIDE]** The universe: S&P 500 members on each date (point-in-time), and the treatment of stocks with incomplete histories.
- Note: CRSP may only run to the end of 2025; confirm once access arrives.

---

## 6. Fixed choices [DECIDE]

- **[DECIDE]** The signal set: which price signals carry over, and the implied-volatility signal with its source.
- **[DECIDE]** Portfolio construction for claim 3: number of holdings, sizing, rebalancing.
- **[DECIDE]** Costs and execution timing. Signals use the official 4pm close, so trades happen on day $t+1$ at the earliest (BACKTESTING.md rule 8).
- **[DECIDE]** Total returns: prices from IVolatility are split-adjusted only; dividends come from `corp-actions` and must be converted to the adjusted price basis (see `DATA.md`). Not needed if CRSP is used.

---

## 7. Run budget and log

- **Maximum 20 runs** for this study before its frozen test, logged in `Documents/runs.csv` with `study = equities`.
- Every run is logged, including failed and duplicate runs. One change per run.
- `check_new_run` is called at the top of every script, before any data is loaded.

---

## 8. Caveats (stated in advance)

- The universe is US large caps, where published anomalies have weakened since publication (BACKTESTING.md rule 25).
- Signals from the same price series are likely to be correlated (the crypto pre-checks found this).
- Implied volatility for sector ETFs is only usable from about April 2000 (`DATA.md`), so the options signal misses the start of the 2000–02 bear market.
- **[DECIDE]** further caveats as the spec is written.

---

## 9. Parked (with the condition for coming back)

- **A cross-sectional version** (ranking stocks against each other): a different hypothesis, so a separate project.
- **ML weighting, information-coefficient weighting, a state-space model, a hidden Markov regime rule:** carried over from the crypto study with the same conditions.
- **The crypto replication:** after this study's frozen test.

---

## 10. Open questions

- WRDS access (requested from QuantSoc, 18/11/26). Fallback date 2026-12-18.
- The fund's mandate in writing: which asset classes it trades, and its rules on shorting stocks.
- The latest date CRSP covers.

---

## 11. Deployment requirements

As in the crypto study (execution, capacity, risk limits, monitoring, independent review, a live record), plus: the PDT rule and minimum account size for frequent stock trading, and borrow availability if shorting is allowed. Worked on only if claim 3 and the frozen test pass.

---

## 12. Results

Results are added here in run order. Nothing above this section is changed because of a result. None yet.