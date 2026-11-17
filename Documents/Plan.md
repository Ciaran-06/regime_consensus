# PLAN.md | regime_consensus | Last updated 17/11/26

High-level steps only. Details live in `NOTES.md` (the spec), `BACKTESTING.md` (the rules) and `DATA.md` (the data).

**Gates** are kill tests. If a gate fails, follow the decision table in NOTES.md section 4. Don't adjust and retry.

---

## Standing rules (every phase)

- Log every run in `runs.csv`, including failures. Budget: 20 runs.
- One change per run.
- Design data only (BTC, ETH) until phase 8. Unseen coins: dates only. Frozen: nothing.
- No spec change after seeing a result it affects.
- Commit before and after each phase.

---

## Phases

- [x] **0. Write the spec.** *So the hypothesis and kill tests are dated before any data.*
- [x] **0b. Download the data.** *Design and unseen coins, 2017–2025, frozen data never requested.*
- [x] **1. Close the spec.** Finish the open `[DECIDE]` and `[DRAFT]` items in NOTES.md. *So every rule is fixed before any result.*
- [x] **2. Finish the data checks.** Clear the `[TODO]`s in DATA.md. *So bad data can't create fake signals.*
- [x] **3. Label regimes and count spells.** *To see whether each state has enough evidence to test, and how long states last.*
- [ ] **4. Build and unit-test the six signals,** with the mean-reversion signs flipped. *So the code matches the spec before it touches returns.*
- [ ] **5. Correlation pre-check.** Drop near-copies by the fixed rule. *So claim 1 tests different signals, not one signal several times.*
- [ ] **6. Claim 1: agreement. GATE.** Majority rule against a single signal. *Does combining signals add anything?*
- [ ] **7. Claim 2: regime dependence. GATE.** Family-by-state table against the predictions. *Is there anything for regimes to exploit?*
- [ ] **8. Claim 3: switching. GATE.** Backtest against both families and the blend, then the deciding unseen coins pooled. *Is there anything to trade after costs?*
- [ ] **9. Frozen 2026 test. GATE.** Opened once. A fail is final. *The last historical check.*
- [ ] **10. Paper trading and deployment requirements.** NOTES.md section 11. *Only live trading is truly out of sample.*
- [ ] **11. Write up.** Every claim, every run and every limitation, whatever the outcome. *A failed test is still a result.*

---

## Where things stand

- **Current phase:** 1 and 2 in parallel.
- **Next action:** find BCH's four missing dates (dates only).