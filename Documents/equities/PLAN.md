# PLAN.md (equities study) | regime_consensus | Last updated 18/11/26

High-level steps only. Details live in `Documents/equities/NOTES.md` (the spec), `Documents/BACKTESTING.md` (the rules) and `Documents/equities/DATA.md` (the data).

**Gates** are kill tests. If a gate fails, follow the decision table in NOTES.md section 4. Don't adjust and retry.

---

## Standing rules (every phase)

- Log every run in `runs.csv` with `study = equities`, including failures. Budget: 20 runs.
- `check_new_run` at the top of every script. One change per run.
- No equity data enters the project's `data/` folder until the data split is fixed. The frozen period is never copied in until the final test.
- No spec change after seeing a result it affects. Every decision dated, with its reason.
- Debug with unit tests, not by rerunning logged scripts.
- Commit before and after each phase.

---

## Phases

- [x] **0. Pivot.** Crypto state tagged `crypto-prechecks-v1`; docs split into `crypto/` and `equities/`; pivot written into NOTES.md section 0. *So the change of design is dated before any equity data.*
- [ ] **1. Infrastructure.** *So both studies share one honest log and the code fits stocks.*
  - [ ] `study` column in `runs.csv`, `log_run`, `check_new_run` and `budget_used`, with tests; existing rows set to `crypto`
  - [ ] Generalise the code: coin → asset; trading-calendar check; lookbacks in trading days; tests updated
- [ ] **2. Data split and universe.** NOTES.md section 5. *So the frozen period is fixed before any data is copied in.*
- [ ] **3. Write the spec.** NOTES.md sections 1, 3, 4 and 6, one decision at a time, each with a source. *So every rule is fixed before any result.*
  - [ ] Literature: the implied-volatility signal; the attention mechanism for equities; confirm the Moskowitz–Grinblatt and Da–Liu–Schaumburg citations
- [ ] **4. Data.** *So bad data can't create fake signals.*
  - [ ] Sector ETFs: prices, dividends, total returns, checks (no WRDS needed)
  - [ ] Stocks: CRSP, historical GICS and the link table, joined to IVolatility by CUSIP (or the fallback, if WRDS has not arrived by 2026-12-18)
  - [ ] Every check and its result recorded in DATA.md
- [ ] **5. Pre-checks.** Regime labels and spell counts; signals and family votes; correlation pre-check. Logged diagnostic runs, each with a prediction written first.
- [ ] **6. Claim 1: agreement. GATE.**
- [ ] **7. Claim 2: regime dependence. GATE.**
- [ ] **8. Claim 3: switching. GATE.**
- [ ] **9. Frozen test. GATE.** Opened once. A fail is final.
- [ ] **10. Paper trading and deployment requirements.**
- [ ] **11. Write up.** Every claim, every run and every limitation, whatever the outcome.
- [ ] **12. Crypto replication,** from `crypto-prechecks-v1`, following `Documents/crypto/NOTES.md`.

---

## Where things stand

- **Current phase:** 1, infrastructure.
- **Next action:** add the `study` column to the run log.
- **Run budget:** 0 of 20 used (equities). Crypto: 6 of 20.
- **Waiting on:** WRDS access from QuantSoc (fallback date 2026-12-18); the fund's mandate in writing.