# regime_consensus

A pre-registered test of whether agreement across momentum and mean-reversion signals, weighted by market regime, predicts BTC and ETH returns after trading costs.

**Status:** spec agreed, data downloaded, no results yet. See [`PLAN.md`](PLAN.md) for progress.

---

## The question

Three claims, tested in order. Each has a kill criterion written before any data was loaded.

1. **Agreement.** When several weak signals point the same way, the returns that follow are better than when acting on a single signal.
2. **Regime dependence.** Which signal family works better (momentum or mean reversion) depends on the market regime, defined by slow and fast trend direction: bull, correction, bear and rebound.
3. **Switching.** Following whichever family suits the current regime beats holding either family all the time, after trading costs.

If a claim fails, the project follows a decision table fixed in advance. It does not adjust and retest.

---

## How the research is run

This project rebuilds an earlier strategy whose design came out of 38 unrecorded backtests. To avoid repeating that:

- **The hypothesis, kill tests and data split were committed before any data was loaded.** The git history dates them.
- **Every rule has a written source:** a paper, a first-principles argument, or "convention, no academic support".
- **Every run is logged,** including failures, with a fixed budget of 20 runs and one change per run.
- **Each claim is decided by one named confirmatory run.** All other runs are diagnostic.
- **Data is split physically by folder:** a design period (2018–2025, BTC and ETH), held-back coins (LTC and BCH deciding; ETC and LINK secondary), and a frozen 2026 test that is opened once.
- **The earlier work is disclosed in full** as an exploratory phase that counts as no evidence.

The rules follow Arnott, Harvey and Markowitz (2019), "A Backtesting Protocol in the Era of Machine Learning".

---

## Documents

| File | Contents |
|---|---|
| [`NOTES.md`](NOTES.md) | The spec: hypothesis, reasoning, regime definitions, kill tests, data split, caveats |
| [`BACKTESTING.md`](BACKTESTING.md) | The 25 rules every test follows |
| [`DATA.md`](DATA.md) | Data source, layout, checks and known gaps |
| [`PLAN.md`](PLAN.md) | Phases and current progress |
| `runs.csv` | Every run, with what changed and the result |

---

## Repository layout

```
regime_consensus/
├── NOTES.md  BACKTESTING.md  DATA.md  PLAN.md  README.md
├── runs.csv
├── pyproject.toml  uv.lock
├── src/regime_consensus/      config (paths and every fixed number), library code
├── scripts/                   numbered pipeline steps
└── data/                      not in git
    ├── raw/                   API responses, never edited
    ├── design/                BTC and ETH, 2017 warm-up + 2018–2025
    ├── unseen/                held-back coins
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

---

## Key references

- Arnott, R., Harvey, C. R., & Markowitz, H. (2019). A Backtesting Protocol in the Era of Machine Learning. *Journal of Financial Data Science*, 1(1), 64–74.
- Goulding, C. L., Harvey, C. R., & Mazzoleni, M. G. (2023). Momentum Turning Points. *Journal of Financial Economics*, 149(3), 378–406.
- Liu, Y., & Tsyvinski, A. (2021). Risks and Returns of Cryptocurrency. *Review of Financial Studies*, 34(6), 2689–2727.
- Nagel, S. (2012). Evaporating Liquidity. *Review of Financial Studies*, 25(7), 2005–2039.
- Hong, H., & Stein, J. C. (1999). A Unified Theory of Underreaction, Momentum Trading, and Overreaction in Asset Markets. *Journal of Finance*, 54(6), 2143–2184.
- Timmermann, A. (2006). Forecast Combinations. *Handbook of Economic Forecasting*, vol. 1.

---

## Disclaimer

This is a research project. Nothing in it is investment advice, and no result here should be read as evidence that a strategy will make money.

**Author:** Ciaran Gaffney ([@Ciaran-06](https://github.com/Ciaran-06))