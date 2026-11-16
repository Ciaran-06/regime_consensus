# NOTES.md | regime_consensus | Last updated 16/11/26

**Status:** Spec nearly complete. No data loaded for V3. Nothing in this file below *Background* has been tested.

The rules every test follows are in `BACKTESTING.md`. Rule numbers below refer to that file.

Markers still open:
- **[DECIDE]** = a choice still to be made before any data is loaded.
- **[DRAFT]** = a proposed wording or number, to confirm or rewrite. Not final until the marker is removed.

---

## 1. Hypothesis

1. **Agreement.** When several weak signals point the same way, the returns that follow are better than when you act on a single signal alone.
   - *Why it should be true:* **[DRAFT]** Each indicator measures the same underlying behaviour with its own error. If those errors are partly independent, requiring agreement filters out false signals that a single indicator would trade on.
   - *Weak point, stated in advance:* the signals are all calculations on the same price series, so their errors may not be independent at all (see Caveats).

2. **Regime dependence.** Which signal family works better depends on the regime. The main test uses four trend states (bull, correction, bear, rebound). High against low volatility is tested separately.
   - *Why it should be true:* **[DRAFT]** Trends persist when information and new buyers arrive gradually. When the short-term move runs against the long-term trend, or when selling is forced, prices overshoot and snap back, which favours mean reversion.

3. **Switching.** Following whichever family suits the current regime beats holding either family all the time, after trading costs.
   - *Why it should be true:* **[DRAFT]** It follows from claim 2, but only if regimes last long enough to be detected in time and the gain is larger than the cost of switching.

The claims build on each other and are tested in order. Claim 3 is only tested if claim 2 passes.

---

## 2. Background (exploratory phase)

The model is being rebuilt from a written hypothesis. **Nothing in this section counts as evidence for the hypothesis.** It is recorded so that the number of earlier attempts is disclosed.

### V1 (original QuantConnect project)
- **31 backtests:** 15 on 27 April 2026, 14 on 14–15 May 2026, and 2 reruns in October 2026.
- **Sharpe range:** −1.75 to 0.94. **Order counts:** 24 to 5,206, so the design itself changed between runs, not only the settings.
- **About 21 distinct configurations.** The rest are duplicate reruns, one run with zero orders and two runtime errors.
- **15 May was a tuning session:** about ten runs in 30 minutes, climbing from 0.69 to 0.94.
- **What changed between runs is not recorded.** QuantConnect stores the code for each backtest, so it is recoverable (see Open questions).
- **Conclusion:** the design came out of a search. A best Sharpe of 0.94 from about 21 tries is close to what luck alone would produce (about 0.7 for the best of 30 zero-edge strategies over eight years).

### V2 (V1's final version with bugs fixed and costs added)
- **Setup:** BTCUSD and ETHUSD, daily bars, Coinbase data, 2018-01-01 to 2026-01-01.
- **Logic:** six scores per coin per day; trade when consensus $\left|\sum s_i\right| / \sum |s_i| > 0.6$, in the direction of the three momentum scores; size $\min(40\%,\ 15\% / \text{vol})$ set at entry; exit on a 5% loss or a signal flip; optional filter (trade only while BTC is above its 200-day average).
- **Bugs fixed from V1:** MACD histogram made unit-free; each coin sized on its own volatility (ETH used BTC's); fees added; benchmark changed to BTC; annualisation changed to 365 days.
- **The three "mean-reversion" signals vote with momentum.** All three are positive when the price is high. V2 is therefore a pure trend-following strategy, and claim 2 has never been tested.
- **7 backtests on 23 October 2026**, varying the regime filter and the fee:

Sharpe ratio by fee per side:

| Regime filter | 0     | 0.001 | 0.0025 | 0.006 |
|---------------|-------|-------|--------|-------|
| On            | 0.871 | 0.797 | 0.676  | 0.367 |
| Off           | –     | 1.068 | 0.927  | 0.571 |

- **Orders:** about 425–560 per run.
- **Best PSR:** 39% (QuantConnect's PSR is the probability that the true Sharpe is above 1.0, not above 0).
- **Filter off scores higher at every fee level, but the difference is not significant.** Paired Ledoit–Wolf and block-bootstrap tests at a 0.1% fee: gain 0.16 Sharpe (1.00 against 0.84, computed without a risk-free rate), 95% range −0.27 to +0.60, p = 0.46. The three fee levels are the same eight years each time, so they are one piece of evidence, not three.
- **The V2 filter was an on/off switch** (cash when BTC was below its 200-day average). Its cost came from blocked trades, so this result says nothing about how well a trend rule labels regimes.
- **Results are fragile to fees.** With the filter off, Sharpe falls from 1.07 to 0.57 as the fee rises from 0.1% to 0.6%.

**Total runs before this spec: 38 visible in QuantConnect** (31 in V1 including the two October reruns, plus 7 in V2). To be checked against `runs.csv`.

---

## 3. Regime definitions

All rules use past data only.

### Trend: four states from a slow and a fast trend
- **Slow trend:** sign of the coin's return over the past 365 days.
- **Fast trend:** sign of the coin's return over the past 30 days.
- **[DRAFT]** the 365 and 30-day lengths follow the 12-month and 1-month convention in Goulding, Harvey and Mazzoleni (2023), "Momentum Turning Points". To confirm against the paper.
- *Reason for this rule over a 200-day average:* a single long average takes months to register a turn. The fast trend flags the turn early. This reason does not depend on any backtest result.

**Predicted better family in each state, written before looking:**

| State | Slow trend | Fast trend | Predicted better family |
|---|---|---|---|
| Bull | up | up | Momentum |
| Correction | up | down | Mean reversion |
| Bear | down | down | Momentum |
| Rebound | down | up | No prediction (reported only) |

- **Bear was changed from mean reversion to momentum on 16/11/26, before any data was loaded.** Reason: the source paper finds that Bear states are followed by negative average returns, which is continuation.
- The same paper favoured faster momentum after Rebound months. Rebound stays "no prediction" unless that is changed before data is loaded.
- **Mean reversion is now predicted in one state only (Correction).** Claim 2 therefore rests on corrections behaving differently from bull and bear markets.
- The paper's evidence is monthly equity-market data. Carrying it to daily crypto is an assumption.

### Volatility: tested separately
- **[DRAFT]** high if 30-day realised volatility is above its own median over the previous 365 days, low otherwise.
- **No prediction was made**, so the volatility result is exploratory. It is reported but cannot count as a pass for claim 2.
- The trend states and the volatility states are never combined into an 8-cell grid.

### Minimum evidence per state
- **A state's result counts only if it has at least 5 spells of at least 20 days each.** A spell is one continuous run of days in that state.
- *Reason:* days inside a spell are not independent. If a family had no real advantage, the chance of it winning 5 spells out of 5 by luck is $\left(\tfrac{1}{2}\right)^5 \approx 3\%$.
- Spells are counted by calendar period across both coins. BTC and ETH move together, so they do not double the count.
- **If a trend state falls short,** it is merged with the state that shares its slow trend (correction into bull, rebound into bear).
- **Check before any returns are used:** count the days and spells in each state.

---

## 4. Kill tests (fixed before any V3 result)

**Each claim is decided by exactly one confirmatory run, named below. Every other run is diagnostic and cannot pass a claim (rule 5).**
- *Reason:* about one in twenty strategies with no edge clears $t = 2$ by luck, and the run budget is 20.
- A confirmatory run that fails because of a bug is logged, fixed and rerun. The rerun only counts if the fix was not chosen by looking at the result.

### Pre-check: are the signals different?
- Correlation matrix of the six daily scores, per coin.
- Reported, not pass/fail. If the signals within a family are nearly identical, claim 1 is tested on what is effectively one signal per family, and that is stated in the write-up.

### Claim 1: agreement
- **Metric:** mean return over the next 5 days after a signal, in the direction the signal points.
- **Comparison:** within each family, a single signal with its threshold set so that it trades on the same number of days as the agreement gate.
- **Sample:** BTC and ETH, design period.
- **Pass:** **[DRAFT]** the agreement gate's mean forward return is higher, with $t > 2$ on the difference (using a method that allows for overlapping 5-day windows).
- **Confirmatory run:** the first complete run of this comparison on the design period, both coins pooled, with the fixed choices in section 6.

### Claim 2: regime dependence
- **Metric:** mean 5-day forward return per signal, for each family in each trend state.
- **Comparison:** the predicted table in section 3.
- **Sample:** BTC and ETH, design period; only states that meet the minimum in section 3.
- **Pass:** **[DRAFT]** in each of the three states with a prediction, the predicted family has the higher mean forward return, and the gap between the families in Correction differs from the gap in Bull and Bear with $t > 2$.
- **Confirmatory run:** the first complete run of the family-by-trend-state table on the design period, both coins pooled.
- **Volatility:** the same table for high and low volatility, reported as exploratory.

### Claim 3: switching
- **Rule:** follow the predicted family in each state. **[DRAFT]** hold no position in a state with no prediction.
- **Metric:** Sharpe ratio after costs at 0.25% per side.
- **Comparison:** the better of the two families held all the time.
- **Sample:** design period, then the unseen coins.
- **Pass:** **[DRAFT]** switching beats both single families on the design period, and the direction holds on the unseen coins.
- **Confirmatory run:** the first complete backtest of the switching rule against both single families at 0.25% per side.
- **Benchmarks reported alongside (rule 15):** holding the coin at the same volatility, the single-signal version, and random entries with the same average exposure and holding time.

### Decision table

| Claim 1 | Claim 2 | Claim 3 | Decision |
|---|---|---|---|
| fail | – | – | Drop the agreement function. Continue with one signal per family. |
| any | fail | – | Stop. No regime switching. Write up the negative result. |
| any | pass | fail | Regimes are real but not tradable after costs. Research paper only, no deployment. |
| any | pass | pass | Continue to the frozen 2026 test, then paper trading. |

**After the frozen 2026 test (rule 16):**

| Frozen test | Decision |
|---|---|
| pass | Paper trading, then the deployment checks in rule 23. |
| fail | The strategy is not adjusted and retested. Write up the result. No deployment. |

---

## 5. Data split

- **Design period:** 2018-01-01 to 2025-12-31. Already seen by V1 and V2, which is stated as a limitation.
- **Warm-up:** data from 2017-01-01, used only to fill the 365-day lookbacks. No results are measured on it.
- **Frozen test:** 2026-01-01 onwards, in a separate file that is not opened until the end. Opened once.
- **Unseen coins:** long-history coins, so they cover both bear markets: LTC, BCH, LINK and ETC, subject to each having data from 2018 on the chosen exchange. **[DECIDE]** final list after the data check, fixed before any V3 result. Downloaded now, not analysed until claim 3.
- **Forward test:** paper trading after the frozen test.

---

## 6. Fixed choices

| Signal | Family | Parameters | Source |
|---|---|---|---|
| RSI relative to 50 | Momentum | 14 days | Standard convention |
| Rate of change | Momentum | average of 5, 10 and 20 days | Range average, so no single value is tuned |
| MACD histogram | Momentum | 12 / 26 / 9 | Standard convention |
| RSI extreme | Mean reversion (sign flipped from V2) | 70 / 30 | Standard convention |
| Bollinger band position | Mean reversion (sign flipped from V2) | 20 days, 2 sd | Standard convention |
| Price z-score | Mean reversion (sign flipped from V2) | average of 20, 50 and 100 days | Range average, so no single value is tuned |

- Agreement is measured **within** each family, because the two families disagree by design in a trend.
- **Agreement threshold:** **[DECIDE]** V2 used 0.6, inherited from V1 with no source. Either give it a source or replace it with a rule that has no number to tune.
- **Costs:** judged at 0.25% per side until the fund confirms its exchange and fee tier. Results are also reported at 0.1% and 0.6%.
- No parameter is tuned on the design period.

---

## 7. Run budget and log

- **Maximum 20 V3 runs** before the frozen 2026 test.
- Every run is logged in `runs.csv` with its date, what changed and its result, including failed and duplicate runs.
- One change per run.

---

## 8. Caveats (stated in advance)

- The design period has already been seen, and I know what worked on it.
- The six signals are all calculations on the same price, so they are probably highly correlated.
- 2018–2025 contains only two or three bear markets, so any regime result rests on a few independent episodes.
- Shorts would need perpetual futures, whose funding costs are not modelled yet.
- The frozen test is under a year of data: enough to catch a disaster, not enough to confirm an edge.
- Several claims are tested, so one passing at $t > 2$ is weaker evidence than a single pre-chosen test.
- One 5-day horizon is used for both families. Momentum may need longer to show, which could bias the comparison against it.
- The unseen coins move with BTC, so they are supporting evidence, not an independent test (rule 17).
- Effects weaken once they are published and traded. Crypto momentum has been public since 2018, so it may already have faded (rule 25).
- Only live or paper trading is truly out of sample, because every historical test is run knowing roughly how history went (rule 18).

---

## 9. Parked (with the condition for coming back)

- **ML weighting of the two families:** only if claim 3 passes with a simple rule, and only if it then beats that rule out of sample.
- **Hidden Markov model as the regime rule:** only if claim 2 passes with the simple rules, tested as one pre-declared change against them.
- **Trend and volatility combined:** only if each passes on its own.
- **Vol-forecast position sizing:** only after claim 3, as one pre-declared change.
- **Funding-rate and intraday data:** only when a passed claim needs them.
- **Other regime definitions:** not added after results are seen.

---

## 10. Open questions

- Which exchange and fee tier would the fund use? **[DECIDE]** date the team lead was asked.
- Did the April–May V1 runs include 2026 data? If so, early 2026 is not unseen.
- Which V1 version was carried into V2? The October reruns (Sharpe 0.533, 425 orders) match the last May run (0.526, 425 orders), not the 0.94 run. To confirm in the code.
- What changed between the V1 runs? Recoverable from QuantConnect's stored code.
- What stop rule applies before deployment (for example a drawdown limit)? It is set from the results, in writing, before paper trading starts (rule 23).