# PLAN.md | regime_consensus | Last updated 18/11/26

High-level steps only. Details live in `NOTES.md` (the spec), `BACKTESTING.md` (the rules) and `DATA.md` (the data).

**Gates** are kill tests. If a gate fails, follow the decision table in NOTES.md section 4. Don't adjust and retry.

---

## Standing rules (every phase)

- Log every run in `runs.csv` with `log_run`, including failures. Budget: 20 runs.
- One change per run.
- Design data only (BTC, ETH) until phase 8. Unseen coins: dates only. Frozen: nothing.
- No spec change after seeing a result it affects.
- Debug with unit tests, not by rerunning logged scripts.
- Commit before and after each phase.

---

## Phases

- [x] **0. Write the spec.** *So the hypothesis and kill tests are dated before any data.*
- [x] **0b. Download the data.** *Design and unseen coins, 2017–2025, frozen data never requested.*
- [x] **1. Close the spec.** Finish the open `[DECIDE]` and `[DRAFT]` items in NOTES.md. *So every rule is fixed before any result.*
- [x] **2. Finish the data checks.** Clear the `[TODO]`s in DATA.md. *So bad data can't create fake signals.*
- [x] **3. Label regimes and count spells.** *To see whether each state has enough evidence to test, and how long states last.*
- [x] **4. Build and unit-test the six signals,** with the mean-reversion signs flipped. *So the code matches the spec before it touches returns.*
  - [x] Signal definitions written in NOTES.md section 6, majority rule confirmed
  - [x] `signals.py`: RSI, EMA, `sign_vote` and all six signals, each with tests
  - [x] `agreement.py`: `count_votes`, `family_vote` and `agreement_rate`, with tests
  - [x] `build_signals`: all six signals and both family votes for every coin, in one table
  - [x] `scripts/02_signals.py`: run R02, `signals` table saved
  - [x] `signals` table documented in DATA.md; agreement rates recorded in NOTES.md section 12
- [ ] **5. Correlation pre-check.** Drop near-copies by the fixed rule. *So claim 1 tests different signals, not one signal several times.*
  - [x] Rule details settled in NOTES.md section 4 (calm/turbulent definition, either coin decides, order of checking)
  - [x] Config: `CORR_THRESHOLD`, `MOMENTUM_PRIORITY`, `REVERSION_PRIORITY`, `VOL_WINDOW`, `VOL_MEDIAN_WINDOW`
  - [x] `label_volatility` in `regime_modeling.py`, with tests
  - [x] `select_signals` in `signal_selection.py`, with tests on hand-made correlation tables
  - [x] Shared test helpers moved to `tests/helpers.py`
  - [x] `scripts/03_correlation.py` (run R03): Spearman correlations of the six scores per coin, for all days, calm days and turbulent days; apply `select_signals` to the all-days tables; save, print what's kept, `log_run`
  - [x] Record the result in NOTES.md section 12; document the saved tables in DATA.md. *Dropped: rate of change (momentum) and Bollinger (mean reversion).*
  - [x] Update `MOMENTUM_SIGNALS` / `REVERSION_SIGNALS` in config, fix any tests that assume three signals per family, then rerun `scripts/02_signals.py` (run R04)
  - [ ] Record R04 against the predictions in NOTES.md section 12; update the `signals` entry in DATA.md
- [ ] **6. Claim 1: agreement. GATE.** Majority rule against a single signal. *Does combining signals add anything?*
  - [ ] Before starting: tests for `trend_sign`, `label_regimes` and `find_spells`
- [ ] **7. Claim 2: regime dependence. GATE.** Family-by-state table against the predictions. *Is there anything for regimes to exploit?*
- [ ] **8. Claim 3: switching. GATE.** Backtest against both families and the blend, then the deciding unseen coins pooled. *Is there anything to trade after costs?*
- [ ] **9. Frozen 2026 test. GATE.** Opened once. A fail is final. *The last historical check.*
- [ ] **10. Paper trading and deployment requirements.** NOTES.md section 11. *Only live trading is truly out of sample.*
- [ ] **11. Write up.** Every claim, every run and every limitation, whatever the outcome. *A failed test is still a result.*

---

## Where things stand

- **Current phase:** 5, correlation pre-check. R03 done: each family keeps two signals (momentum: MACD, RSI relative to 50; mean reversion: z-score, RSI extreme). 63 tests passing.
- **Next action:** rebuild the family votes with the kept signals (R04). Predictions are already written in NOTES.md section 12; check them before running.
- **Run budget:** 3 of 20 used (R01, R02, R03).
- **Waiting on:** the team lead's confirmation that the fund trades through Alpaca, at tier 1, with no shorting (NOTES.md section 10).