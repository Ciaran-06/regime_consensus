# regime_consensus

A pre-registered test of whether agreement across momentum and mean-reversion signals, weighted by market regime, predicts BTC and ETH returns after trading costs.

**Status:** spec agreed, data downloaded and checked, regime labels and signals built. Correlation pre-check done: two signals per family kept (rate of change and Bollinger dropped as near-copies). No claim tested yet. See [`Documents/PLAN.md`](Documents/PLAN.md) for progress.

---

## The question

Three claims, tested in order. Each has a kill criterion written before any data was loaded.

1. **Agreement.** When several weak signals point the same way, the returns that follow are better than when acting on a single signal.
2. **Regime dependence.** Which signal family works better (momentum or mean reversion) depends on the market regime, defined by slow and fast trend direction: bull, correction, bear and rebound.
3. **Switching.** Following whichever family suits the current regime beats holding either family all the time, after trading costs, trading long or flat only (the fund's broker cannot short crypto).

If a claim fails, the project follows a decision table fixed in advance. It does not adjust and retest.

---

## How the research is run

This project rebuilds an earlier strategy whose design came out of 38 unrecorded backtests. To avoid repeating that:

- **The hypothesis, kill tests and data split were committed before any data was loaded.** The git history dates them.
- **Every rule has a written source:** a paper, a first-principles argument, or "convention, no academic support".
- **Every run is logged** by the scripts themselves (`regime_consensus.runlog`), including failures, with a fixed budget of 20 runs and one change per run.
- **Every signal and label is unit-tested,** including a test that changing future prices cannot change today's value.
- **Each claim is decided by one named confirmatory run.** All other runs are diagnostic.
- **Data is split physically by folder:** a design period (2018–2025, BTC and ETH), held-back coins (LTC and BCH deciding; ETC and LINK secondary), and a frozen 2026 test that is opened once.
- **The earlier work is disclosed in full** as an exploratory phase that counts as no evidence.

The rules follow Arnott, Harvey and Markowitz (2019), "A Backtesting Protocol in the Era of Machine Learning".

---

## Documents

| File | Contents |
|---|---|
| [`Documents/NOTES.md`](Documents/NOTES.md) | The spec: hypothesis, reasoning, regime definitions, kill tests, data split, caveats |
| [`Documents/BACKTESTING.md`](Documents/BACKTESTING.md) | The 25 rules every test follows |
| [`Documents/DATA.md`](Documents/DATA.md) | Data source, layout, checks and known gaps |
| [`Documents/PLAN.md`](Documents/PLAN.md) | Phases and current progress |
| [`Documents/runs.csv`](Documents/runs.csv) | Every run, with what changed and the result |

---

## Repository layout

```
regime_consensus/
├── README.md
├── Documents/
│   ├── NOTES.md  BACKTESTING.md  DATA.md  PLAN.md
│   └── runs.csv               the run log
├── pyproject.toml  uv.lock
├── src/regime_consensus/
│   ├── config.py              paths and every fixed number from the spec
│   ├── io.py                  loading and saving; guards unseen and frozen data
│   ├── runlog.py              writes runs.csv and enforces the run budget
│   ├── regime_modeling.py     trend signs, regime labels, spells, volatility labels
│   ├── signals.py             the six signals and the signals table
│   ├── agreement.py           family votes (majority rule) and agreement rates
│   └── signal_selection.py    correlation pre-check: drops near-copy signals
├── scripts/                   numbered pipeline steps (00_download, 01_regimes, ...)
├── Notebooks/                 data checks and exploration
├── tests/                     unit tests
└── data/                      not in git
    ├── raw/                   API responses, never edited
    ├── design/                BTC and ETH, 2017 warm-up + 2018–2025
    ├── unseen/                held-back coins
    ├── derived/               processed tables (regime labels, signals, volatility, correlations)
    └── frozen/                2026, empty until the final test
```

---

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/Ciaran-06/regime_consensus.git
cd regime_consensus
uv sync
```

Download the data (daily candles from Coinbase's public API; no account or key needed):

```bash
uv run python scripts/00_download.py
```

The script never requests data after 2025-12-31, so the frozen test set is not downloaded.

Run the tests, then the pipeline in order (each script is a logged run, so rerunning one adds a row to `runs.csv` and uses budget):

```bash
uv run pytest
uv run python scripts/01_regimes.py
uv run python scripts/02_signals.py
uv run python scripts/03_correlation.py
```

---

## Key references

- Arnott, R., Harvey, C. R., & Markowitz, H. (2019). A Backtesting Protocol in the Era of Machine Learning. *Journal of Financial Data Science*, 1(1), 64–74.
- Goulding, C. L., Harvey, C. R., & Mazzoleni, M. G. (2023). Momentum Turning Points. *Journal of Financial Economics*, 149(3), 378–406.
- Liu, Y., & Tsyvinski, A. (2021). Risks and Returns of Cryptocurrency. *Review of Financial Studies*, 34(6), 2689–2727.
- Nagel, S. (2012). Evaporating Liquidity. *Review of Financial Studies*, 25(7), 2005–2039.
- Hong, H., & Stein, J. C. (1999). A Unified Theory of Underreaction, Momentum Trading, and Overreaction in Asset Markets. *Journal of Finance*, 54(6), 2143–2184.
- Timmermann, A. (2006). Forecast Combinations. *Handbook of Economic Forecasting*, vol. 1.
- Dietterich, T. G. (2000). Ensemble Methods in Machine Learning. *Multiple Classifier Systems*, Lecture Notes in Computer Science 1857.
- Wilder, J. W. (1978). *New Concepts in Technical Trading Systems*.

---

## Disclaimer

This is a research project. Nothing in it is investment advice, and no result here should be read as evidence that a strategy will make money.

**Author:** Ciaran Gaffney ([@Ciaran-06](https://github.com/Ciaran-06))