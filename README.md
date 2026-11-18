# regime_consensus

A pre-registered test of whether agreement between trading signals predicts returns, whether the best signal family depends on the market regime, and whether switching between families by regime pays after costs. The primary study is on US equities; a crypto study (BTC and ETH) is its out-of-asset-class replication.

**Status:** the equities study was opened on 18/11/26 and its spec is being written. No equity data has been loaded and no claim has been tested. The crypto study is paused after its pre-checks (runs R01–R06, no forward returns computed) and is tagged as `crypto-prechecks-v1`. See [`Documents/equities/PLAN.md`](Documents/equities/PLAN.md) for progress.

---

## The question

Three claims, tested in order. Each has a kill test written before any data is used.

1. **Agreement.** When several weak signals on a stock point the same way, its returns afterwards are better than when acting on any one of those signals alone.
2. **Regime dependence.** Which signal family (momentum or mean reversion) works better on a stock depends on the trend regime of its **sector**: bull, correction, bear or rebound.
3. **Switching.** A portfolio that follows, for each stock, the family its sector's regime predicts beats holding either family all the time, after trading costs.

If a claim fails, the project follows a decision table fixed in advance. It does not adjust and retest.

**Why sectors:** much of stock momentum comes from industry momentum, while short-term reversal is strongest once industry moves are removed. So the signals come from the stock, and the regime comes from its sector, measured on the sector SPDR ETFs.

---

## How the research is run

- **Every rule is written, sourced and dated before the result it affects.** The git history dates them.
- **The most rigorous option is chosen for every decision:** the best available data, the fewest free choices, and everything fixed in advance.
- **Point-in-time data:** the S&P 500 universe as it was on each date (including stocks later delisted), delisting returns, and sector classifications as they were at the time (primary source: CRSP and Compustat via WRDS).
- **Every run is logged** by the scripts themselves (`regime_consensus.runlog`), including failures, with a fixed budget of 20 runs per study, one change per run, and a check that refuses accidental duplicate runs.
- **Each claim is decided by one named confirmatory run.** All other runs are diagnostic.
- **A frozen test period is opened once, at the end.**
- **Earlier work is disclosed in full,** including the crypto study's history and what had already been seen in the equity data.

The rules follow Arnott, Harvey and Markowitz (2019), "A Backtesting Protocol in the Era of Machine Learning".

---

## Documents

| File | Contents |
|---|---|
| [`Documents/equities/NOTES.md`](Documents/equities/NOTES.md) | Equities spec (primary): the pivot, hypothesis, regimes, kill tests, data split, caveats |
| [`Documents/equities/DATA.md`](Documents/equities/DATA.md) | Equity data sources, facts and checks |
| [`Documents/equities/PLAN.md`](Documents/equities/PLAN.md) | Equities phases and progress |
| [`Documents/crypto/NOTES.md`](Documents/crypto/NOTES.md) | Crypto spec (replication), with runs R01–R06 and the status at pause |
| [`Documents/crypto/DATA.md`](Documents/crypto/DATA.md) | Crypto data sources and checks |
| [`Documents/crypto/PLAN.md`](Documents/crypto/PLAN.md) | Crypto phases |
| [`Documents/BACKTESTING.md`](Documents/BACKTESTING.md) | The 25 rules every test follows (both studies) |
| [`Documents/runs.csv`](Documents/runs.csv) | Every run in both studies, with what changed and the result |

---

## Repository layout

```
regime_consensus/
├── README.md
├── Documents/
│   ├── BACKTESTING.md  runs.csv     shared by both studies
│   ├── equities/                    NOTES.md  DATA.md  PLAN.md
│   └── crypto/                      NOTES.md  DATA.md  PLAN.md
├── pyproject.toml  uv.lock
├── src/regime_consensus/
│   ├── config.py              paths and every fixed number from the spec
│   ├── io.py                  loading and saving; guards unseen and frozen data
│   ├── runlog.py              writes runs.csv, enforces the budget, refuses duplicates
│   ├── regime_modeling.py     trend signs, regime labels, spells, volatility labels
│   ├── signals.py             signals and the signals table
│   ├── agreement.py           family votes and agreement rates
│   └── signal_selection.py    correlation pre-check: drops near-copy signals
├── scripts/                   numbered pipeline steps
├── Notebooks/                 data checks and exploration
├── tests/                     unit tests
└── data/                      not in git (licensed data is never committed)
```

The code was written for the crypto study and is being generalised for equities (assets instead of coins, a trading-day calendar, lookbacks in trading days).

---

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/Ciaran-06/regime_consensus.git
cd regime_consensus
uv sync
uv run pytest
```

Equity data comes from licensed sources (CRSP and Compustat via WRDS, and IVolatility) and is not included. The crypto study's data can be downloaded from Coinbase's public API with `uv run python scripts/00_download.py`. Every pipeline script is a logged run, so running one adds a row to `runs.csv` and uses budget.

---

## Key references

- Arnott, R., Harvey, C. R., & Markowitz, H. (2019). A Backtesting Protocol in the Era of Machine Learning. *Journal of Financial Data Science*, 1(1), 64–74.
- Bhojraj, S., Lee, C. M. C., & Oler, D. K. (2003). What's My Line? A Comparison of Industry Classification Schemes for Capital Market Research. *Journal of Accounting Research*, 41(5), 745–774.
- Campbell, J. Y., Grossman, S. J., & Wang, J. (1993). Trading Volume and Serial Correlation in Stock Returns. *Quarterly Journal of Economics*, 108(4), 905–939.
- Dietterich, T. G. (2000). Ensemble Methods in Machine Learning. *Multiple Classifier Systems*, Lecture Notes in Computer Science 1857.
- Goulding, C. L., Harvey, C. R., & Mazzoleni, M. G. (2023). Momentum Turning Points. *Journal of Financial Economics*, 149(3), 378–406.
- Nagel, S. (2012). Evaporating Liquidity. *Review of Financial Studies*, 25(7), 2005–2039.
- Smith, J., & Wallis, K. F. (2009). A Simple Explanation of the Forecast Combination Puzzle. *Oxford Bulletin of Economics and Statistics*, 71(3), 331–355.
- Timmermann, A. (2006). Forecast Combinations. *Handbook of Economic Forecasting*, vol. 1.
- Wilder, J. W. (1978). *New Concepts in Technical Trading Systems*.

---

## Disclaimer

This is a research project. Nothing in it is investment advice, and no result here should be read as evidence that a strategy will make money.

**Author:** Ciaran Gaffney ([@Ciaran-06](https://github.com/Ciaran-06))