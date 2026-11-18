# NOTES.md | regime_consensus | Last updated 18/11/26 (pre-check details settled)

**Status:** Spec agreed on 16/11/26; all `[DRAFT]` items closed on 17/11/26. Data downloaded and checked. Regime labels built (run R01, 17/11/26). Six signals and both family votes built (run R02, 18/11/26). No forward returns computed yet. Results are recorded in section 12 as they come in.

The rules every test follows are in `BACKTESTING.md`. Rule numbers below refer to that file.

---

## 1. Hypothesis

1. **Agreement.** When several weak signals point the same way, the returns that follow are better than when you act on a single signal alone.
   - *Why it should be true:* Each signal is partly right and partly wrong. If their mistakes are largely independent, agreement between them raises confidence, because it is unlikely that all of them are wrong in the same direction at once.
   - *What this needs:* each signal must carry some real information on its own, and their errors must be as weakly correlated as realistically possible.
   - *Type of claim:* this is a claim about a method, so its reason is statistical. There is no losing side of a trade to name.
   - *Sources:* the forecast-combination literature: Timmermann (2006), "Forecast Combinations", in the *Handbook of Economic Forecasting*, volume 1. Ensemble voting: Dietterich (2000), "Ensemble Methods in Machine Learning", *Multiple Classifier Systems*, Lecture Notes in Computer Science 1857: a majority vote beats its members when each is better than chance and their errors are diverse. (Dietterich reference from memory; check before citing.)
   - *Weak point, stated in advance:* the six V2 signals are all calculations on the same price series, so their errors may not be independent at all (see Caveats).

2. **Regime dependence.** Which signal family works better depends on the regime. The main test uses four trend states (bull, correction, bear, rebound). High against low volatility is tested separately.
   - *Why trends continue (Bull, Bear): attention.* Price moves attract attention, and attention brings in new buyers (or, in a fall, new sellers), which pushes the price further in the same direction.
     - *Who is on the wrong side:* whoever traded against the trend: those who sold early in a rise, and those who bought the dip too early in a fall.
     - *Source:* Liu and Tsyvinski (2021), *Review of Financial Studies* 34(6): crypto returns show strong time-series momentum, and proxies for investor attention forecast future returns.
   - *Why a dip in an uptrend recovers (Correction): payment for providing liquidity.* Sellers who need to get out quickly, such as those panicking, stopped out or liquidated, accept a worse price. Buyers who take the other side are rewarded when the price recovers.
     - *Who is on the wrong side:* the forced and panicked sellers.
     - *Source:* Nagel (2012), *Review of Financial Studies* 25(7): returns to short-term reversal strategies act as a reward for providing liquidity, and they are largest in turbulent markets.
   - *Mechanisms considered and dropped on 17/11/26:* gradual absorption of news (Hong and Stein, 1999), because it was built for stocks, where news such as earnings exists; and forced liquidations, because no peer-reviewed source has been read. They are not used to explain any result after the fact.
   - *Limit of both sources:* Nagel's evidence is on stocks, and Liu and Tsyvinski's sample ends years before the design period does. Applying them to 2018–2025 daily crypto is an assumption.
   - *Weak point, stated in advance:* a correction and the start of a bear market look the same at the time. The Correction prediction loses exactly when the dip turns out to be the start of a bear market.

3. **Switching.** Following whichever family suits the current regime beats holding either family all the time, after trading costs, trading long or flat only.
   - *Why it should be true:* it follows from claim 2, but only if three conditions hold.
     1. **Detection in time.** The regime has to be recognised early enough to act on. The fast trend is built from 30 days of returns, so a change of state can take weeks to show up.
     2. **Persistence.** A state has to last long enough after it is detected for the switch to pay off.
     3. **Costs.** The gain from switching has to be larger than the fees paid on every switch, including switches that turn out to be false alarms.
   - *Who is on the wrong side:* the same traders as in claim 2. Switching adds no new mechanism.
   - *Weak point, stated in advance:* each of the three conditions can fail on its own.

The claims build on each other and are tested in order. Claim 3 is only tested if claim 2 passes.

**Long or flat, decided 17/11/26 before any V3 result.** The fund trades through Alpaca, which does not offer margin or short selling for crypto. Claims 1 and 2 are statements about the market, so they test signals in both directions. Claim 3 is the tradable strategy, so it holds the coin or holds cash, never a short. The reason is the broker's constraint, not any earlier backtest result.

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
- The 365 and 30-day lengths follow the 12-month and 1-month convention in Goulding, Harvey and Mazzoleni (2023), "Momentum Turning Points", converted to days. Confirmed from summaries of the paper; the full text has not been read yet.
- *Reason for this rule over a 200-day average:* a single long average takes months to register a turn. The fast trend flags the turn early. This reason does not depend on any backtest result.
- **Ties:** a trend return of exactly zero counts as down (−1), because a flat price is not evidence of an uptrend. Decided 17/11/26, before labelling. The number of ties is counted once the labels are built and recorded in `DATA.md`.
- **Warm-up days:** a day without a full lookback has no sign and no state. It is never labelled up or down by default.

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
- High if 30-day realised volatility is above its own median over the previous 365 days, low otherwise.
- **No prediction was made**, so the volatility result is exploratory. It is reported but cannot count as a pass for claim 2.
- The trend states and the volatility states are never combined into an 8-cell grid.

### Minimum evidence per state
- **A state's result counts only if it has at least 5 spells of at least 20 days each.** A spell is one continuous run of days in that state.
- *Reason:* days inside a spell are not independent. If a family had no real advantage, the chance of it winning 5 spells out of 5 by luck is $\left(\tfrac{1}{2}\right)^5 \approx 3\%$.
- **Spells are counted per coin:** each coin must have at least 5 long spells in a state on its own. BTC and ETH move together, so their spells are not added together.
  - *Note:* this wording was settled on 17/11/26, after the spell count. Before that the spec said only "counted by calendar period across both coins". It does not change the outcome: every state passes for each coin separately, and therefore also under BTC alone (section 12).
- **If a trend state falls short,** it is merged with the state that shares its slow trend (correction into bull, rebound into bear).
- **Check before any returns are used:** count the days and spells in each state, and record the typical spell length. Spell length is the first evidence on whether states last long enough for claim 3. Done in run R01; see section 12.

---

## 4. Kill tests (fixed before any V3 result)

**Each claim is decided by exactly one confirmatory run, named below. Every other run is diagnostic and cannot pass a claim (rule 5).**
- *Reason:* about one in twenty strategies with no edge clears $t = 2$ by luck, and the run budget is 20.
- A confirmatory run that fails because of a bug is logged, fixed and rerun. The rerun only counts if the fix was not chosen by looking at the result.

### Pre-check: are the signals different?
- Rank-correlation matrix of the six daily scores, per coin, on the design period. Also computed separately for calm and turbulent periods, because signals tend to move together in a crash.
- **Selection rule, fixed in advance:** two signals in the same family with a correlation above 0.7 are treated as near-copies, and one is dropped.
  - *Reason for 0.7:* at 0.7 two signals share about half their variation ($0.7^2 = 0.49$).
  - *Which one is kept:* the signal with the longer lookback, since longer windows are less noisy. Momentum order: MACD, then rate of change, then RSI. Mean-reversion order: z-score, then Bollinger band position, then RSI extreme.
- **If a family is left with two signals,** it agrees when both point the same way.
- **If a family is left with one signal,** claim 1 cannot be tested in that family, and the signal pool is widened from other types of data (see Parked).
- This step uses no returns. It is logged in `runs.csv` as a diagnostic run.

**Details settled 18/11/26, before any correlation was computed:**
- **Calm and turbulent periods** use the volatility rule in section 3: turbulent if 30-day realised volatility is above its own median over the previous 365 days, calm otherwise. These two matrices are **reported only**; the decision uses the full design period.
- **Either coin decides:** two signals are near-copies if their correlation is above 0.7 on **either** BTC or ETH. *Reason:* one set of signals is used for both coins, and the rule exists to stop one signal being counted twice, so it errs towards dropping.
- **Order of checking:** within each family, go down the priority order (momentum: MACD, rate of change, RSI; mean reversion: z-score, Bollinger, RSI extreme). Keep each signal unless it is a near-copy of a signal already kept. *Reason:* gives the same answer however many signals are correlated with each other.
- **If a signal is dropped:** it is removed from `MOMENTUM_SIGNALS` or `REVERSION_SIGNALS` in `config.py`, and the family votes are rebuilt. The rebuild is a logged diagnostic run.

### Claim 1: agreement
- **Metric:** mean return over the next 5 days after a signal, in the direction the signal points.
- **Comparison:** within each family, a single signal with its threshold set so that it trades on the same number of days as the agreement gate.
- **Sample:** BTC and ETH, design period.
- **Pass:** the majority rule's mean forward return is higher, with $t > 2$ on the difference (using a method that allows for overlapping 5-day windows).
- **Confirmatory run:** the first complete run of this comparison on the design period, both coins pooled, with the fixed choices in section 6.

### Claim 2: regime dependence
- **Metric:** mean 5-day forward return per signal, for each family in each trend state.
- **Comparison:** the predicted table in section 3.
- **Sample:** BTC and ETH, design period; only states that meet the minimum in section 3.
- **Pass:** in each of the three states with a prediction, the predicted family has the higher mean forward return, and the gap between the families in Correction differs from the gap in Bull and Bear with $t > 2$.
- **Confirmatory run:** the first complete run of the family-by-trend-state table on the design period, both coins pooled.
- **Volatility:** the same table for high and low volatility, reported as exploratory.

### Claim 3: switching
- **Rule:** follow the predicted family in each state, long or flat only: when the family points up, hold the coin; when it points down or does not agree, hold cash. Hold cash in a state with no prediction.
  - *Consequence, stated in advance:* in Bear the predicted family is momentum, which mostly points down, so the strategy will mostly hold cash in bear markets.
- **Metric:** Sharpe ratio after costs at 0.25% per side.
- **Comparison:** the better of the two families held all the time.
- **Sample:** design period, then the deciding unseen coins (LTC and BCH) pooled together.
- **Pass:** switching beats both single families and the static blend on the design period, and the same holds on the deciding unseen coins pooled together. The secondary coins (ETC and LINK) are reported but do not count.
  - *Weak point, stated in advance:* this asks only for a higher Sharpe, with no significance test, because eight years of data cannot prove a Sharpe difference. The frozen test and paper trading exist for that reason.
- **Confirmatory run:** the first complete backtest of the switching rule against both single families and the static blend at 0.25% per side.
- **Benchmarks reported alongside (rule 15):** holding the coin at the same volatility, the single-signal version, and random entries with the same average exposure and holding time.
- **Benchmark:** a static 50/50 blend of the slow and fast trend signals (Goulding, Harvey and Mazzoleni, 2023). Switching must beat this as well as both single families.
- **All claim 3 comparisons are long or flat** (the single families, the blend and random entries), so every strategy faces the same constraint.
  - *Reason:* the blend is the simpler model from the same paper. If switching cannot beat it, the regime machinery adds nothing (rule 13).

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
- **Source:** Coinbase public Exchange API, daily candles (one per UTC day), downloaded on 16/11/26. Provisional until the fund confirms its exchange. Details are in `DATA.md`.
- **Unseen coins, fixed on 16/11/26 from first dates only. No prices were looked at.**
  - **Deciding tier: LTC and BCH.** Both pass the rule written in advance (data from 2018): LTC starts 2017-01-01 and BCH starts 2017-12-20. Because of the fork rule below, BCH's regime labels start on 2019-11-20.
  - **Secondary tier: ETC (from 2018-08-08) and LINK (from 2019-06-27).** Reported alongside, but they cannot decide any claim, because they start too late to cover the 2018 bear market.
  - **Pooling:** the deciding coins are pooled together. A result is not required on each coin separately.
  - **BCH fork rule, decided 17/11/26 from dates only:** BCH's four missing days are 2018-11-16 to 2018-11-19, when Coinbase paused trading around the Bitcoin Cash split of 15 November 2018. BCH is treated as a new coin from 2018-11-20, the first day of trading after the gap. No data before that date is used for BCH, and its 365-day warm-up restarts, so its regime labels start on 2019-11-20.
    - *Reason:* before the split one BCH entitled the holder to both resulting coins, and after it only to one. A return or trend that spans the split compares two different assets, like a spin-off. A narrow exclusion window would remove the fake 5-day returns but leave a year of 365-day trend labels built on that comparison.
    - *Cost:* about a year of BCH is lost. Little of the 2018 bear market is affected, because BCH's labels would only have started in December 2018 anyway.
  - Not analysed until claim 3.
- **Forward test:** paper trading after the frozen test.

---

## 6. Fixed choices

### Signal Definitions

**Shared rules (apply to all six)**
- **Input:** daily closes of one coin, from `load_clean`. Each score on day $t$ uses closes up to and including day $t$ only.
- **Sign convention:** a positive score means "expect the price to rise". Mean-reversion scores are flipped so this holds for them too.
- **Vote:** +1, −1, or no reading. Only votes are used by the majority rule; scores are used by the correlation pre-check and the single-signal comparison in claim 1.
- **No reading** also applies to any day without enough history.

| Signal | Family | Parameters | Source |
|---|---|---|---|
| RSI relative to 50 | Momentum | 14 days | Standard convention |
| Rate of change | Momentum | average of 5, 10 and 20 days | Range average, so no single value is tuned |
| MACD histogram | Momentum | 12 / 26 / 9 | Standard convention |
| RSI extreme | Mean reversion (sign flipped from V2) | 70 / 30 | Standard convention |
| Bollinger band position | Mean reversion (sign flipped from V2) | 20 days, 2 sd | Standard convention |
| Price z-score | Mean reversion (sign flipped from V2) | average of 20, 50 and 100 days | Range average, so no single value is tuned |

Notation: $C_t$ is the close on day $t$. $\text{SMA}_n$ and $\sigma_n$ are the mean and standard deviation of the last $n$ closes, including day $t$ (population standard deviation). $\text{EMA}_n$ is an exponential moving average with span $n$.
#### 1. RSI relative to 50 (momentum)
- **RSI:** Wilder's 14-day RSI. $\text{RSI}_t = 100 - \dfrac{100}{1 + G_t / L_t}$, where $G_t$ and $L_t$ are Wilder-smoothed averages of daily gains and losses (smoothing factor $1/14$).
- **Score:** $s_t = (\text{RSI}_t - 50)/50$, between −1 and +1.
- **Vote:** +1 if $\text{RSI}_t > 50$, −1 if below. No reading at exactly 50.
- **History needed:** 14 days.
- **Flat price:** if the price does not move at all, $G_t = L_t = 0$ and RSI is $0/0$. RSI is then NaN (no reading), not 50, so that missing information is never given a value. Decided 17/11/26, before any signal was computed. It gives no vote either way, since signals 1 and 4 both have no reading at RSI 50.
- **Source:** Wilder (1978), *New Concepts in Technical Trading Systems*. Standard convention.

#### 2. Rate of change (momentum)
- **Score:** the average of the 5, 10 and 20-day simple returns: $s_t = \tfrac{1}{3}\sum_{k \in \{5,10,20\}} \left(\dfrac{C_t}{C_{t-k}} - 1\right)$.
- **Vote:** the sign of $s_t$. No reading at exactly zero.
- **History needed:** 20 days.
- **Source:** range average, so no single lookback is tuned.

#### 3. MACD histogram (momentum)
- **MACD line:** $M_t = \text{EMA}_{12}(C)_t - \text{EMA}_{26}(C)_t$. **Signal line:** $S_t = \text{EMA}_9(M)_t$.
- **Score:** $s_t = (M_t - S_t)/C_t$. Dividing by the price makes it unit-free (the V2 bug fix).
- **Vote:** the sign of $s_t$. No reading at exactly zero.
- **History needed:** 34 days (26 for the MACD line, then 9 for its signal line).
- **Source:** Appel's MACD. Standard convention.
- *Note:* the histogram is positive when the trend is **strengthening**, not simply when price is rising, so it can disagree with the other two momentum signals during a slowing uptrend.

#### 4. RSI extreme (mean reversion)
- **RSI:** the same 14-day RSI as signal 1.
- **Score:** how far RSI is beyond its threshold, flipped: $s_t = (30 - \text{RSI}_t)/30$ if $\text{RSI}_t < 30$; $s_t = -(\text{RSI}_t - 70)/30$ if $\text{RSI}_t > 70$; $s_t = 0$ otherwise.
- **Vote:** +1 if $\text{RSI}_t < 30$ (oversold, expect a bounce), −1 if $\text{RSI}_t > 70$. **No reading between 30 and 70.**
- **History needed:** 14 days.
- **Source:** Wilder (1978): 70 and 30 are the standard overbought and oversold levels.

#### 5. Bollinger band position (mean reversion)
- **Bands:** middle $\text{SMA}_{20}$, upper and lower $\text{SMA}_{20} \pm 2\sigma_{20}$.
- **Score:** distance from the middle in half band-widths, flipped: $s_t = -\dfrac{C_t - \text{SMA}_{20}}{2\sigma_{20}}$.
- **Vote:** +1 if $C_t$ is below the lower band, −1 if above the upper band. **No reading inside the bands.**
- **History needed:** 20 days.
- **Source:** Bollinger (2001), *Bollinger on Bollinger Bands*. Standard convention.

#### 6. Price z-score (mean reversion)
- **Score:** the average of three z-scores, flipped: $s_t = -\tfrac{1}{3}\sum_{n \in \{20,50,100\}} \dfrac{C_t - \text{SMA}_n}{\sigma_n}$.
- **Vote:** the sign of $s_t$. No reading at exactly zero.
- **History needed:** 100 days.
- **Source:** range average, so no single lookback is tuned.

#### Consequences of these definitions, found before any signal was computed

These follow from the formulas alone, not from data.

1. **Bollinger position is the 20-day z-score in disguise.** Its score equals $-\tfrac{1}{2} \times$ the 20-day z-score, which is one of the three parts of signal 6. The two will be highly correlated, so the pre-check will very likely drop Bollinger (z-score is kept by the fixed order). They differ only in voting: Bollinger votes only outside the bands, z-score always.
2. **The momentum family always has a majority.** All three momentum signals vote nearly every day, and three votes of ±1 always contain a 2-of-3 majority. So for momentum the agreement rule never filters anything: it only decides the direction.
3. **The mean-reversion family rarely agrees.** Z-score votes every day, but RSI extreme and Bollinger vote only in the tails. A majority needs z-score plus one of the rare signals, so mean reversion speaks on a small share of days.
4. **RSI is shared across families.** Signals 1 and 4 use the same RSI, so in the tails they always disagree. This is by design: they read the same number as continuation or reversal.

**Decided 17/11/26, before any signal was computed:** keep the six signals and the majority rule, accepting points 1–3.
- *Reason:* a majority vote is the standard way to combine an ensemble of voters, and it has no number to tune (Dietterich, 2000). Bollinger stays in because the correlation pre-check was set up in advance to handle near-duplicates.
- *Consequence for claim 1, stated in advance:* in the momentum family the agreement gate is open almost every day, so claim 1 there tests whether the majority **direction** beats a single signal's direction, not whether agreement picks better days to trade. In the mean-reversion family the gate is open only when a tail signal fires, so there it does act as a filter.
- *Alternatives considered:* requiring all voting signals to agree, and adding a fourth signal per family with a 3-of-4 rule. Not taken. A fourth price-based signal would likely be another near-copy, which fails Dietterich's diversity condition; that idea belongs to the wider signal pool in section 9.

- Agreement is measured **within** each family, because the two families disagree by design in a trend.
- **Agreement rule:** a family agrees when at least two of its three signals point the same way. A signal giving no reading counts for neither side.
  - *Reason:* a majority rule has no number to tune. It replaces the 0.6 threshold from V2, which was inherited from the V1 search with no source.
  - *Weak point, stated in advance:* a majority is a weaker form of agreement than all signals agreeing, so it is harder to tell apart from a single signal.
- **Costs:** 0.25% per side, Alpaca's tier 1 taker fee (30-day crypto volume under $100,000). Taker, because orders at the daily close are market orders; the 0.15% maker fee would need limit orders that may not fill. Results are also reported at 0.1% and 0.6%. The bid–ask spread is extra, and is checked before deployment (section 11).
- No parameter is tuned on the design period.

---

## 7. Run budget and log

- **Maximum 20 V3 runs** before the frozen 2026 test.
- Every run is logged in `runs.csv` with its date, what changed and its result, including failed and duplicate runs.
- One change per run.
- `runs.csv` is stored in the `Documents` folder and written with `log_run` from `regime_consensus.runlog`, which numbers runs and enforces the budget.

---

## 8. Caveats (stated in advance)

- The design period has already been seen, and I know what worked on it.
- The six signals are all calculations on the same price, so they are probably highly correlated.
- 2018–2025 contains only two or three bear markets, so any regime result rests on a few independent episodes.
- Claim 3 is long or flat because the fund's broker cannot short crypto. Results from claims 1 and 2 on falling-price signals therefore cannot be traded by the fund.
- The frozen test is under a year of data: enough to catch a disaster, not enough to confirm an edge.
- Several claims are tested, so one passing at $t > 2$ is weaker evidence than a single pre-chosen test.
- One 5-day horizon is used for both families. Momentum may need longer to show, which could bias the comparison against it.
- The unseen coins move with BTC, so they are supporting evidence, not an independent test (rule 17). The two deciding coins, LTC and BCH, are both close relatives of Bitcoin, which makes them the least independent test available.
- LTC and BCH are less liquid than BTC, so real trading costs on them would be higher than the 0.25% assumed.
- Effects weaken once they are published and traded. Crypto momentum has been public since 2018, so it may already have faded (rule 25).
- Only live or paper trading is truly out of sample, because every historical test is run knowing roughly how history went (rule 18).

---

## 9. Parked (with the condition for coming back)

- **ML weighting of the two families:** only if claim 3 passes with a simple rule, and only if it then beats that rule out of sample.
- **Weighting signals by their information coefficient** (the correlation between a signal's score and the return that follows) in place of the agreement rule: only if claim 1 passes with the agreement rule. Weights estimated on past data only, refitted on an expanding window; one pre-declared run, counted in the budget; it must beat the agreement rule out of sample.
  - *Stated in advance:* the "forecast combination puzzle" (Timmermann, 2006) is that estimated weights often lose to equal weights out of sample, because the weights are noisy. So this is a real test, not an expected improvement.
- **A state-space model of the signals in place of the agreement rule:** only if claim 1 passes with the agreement rule. Each signal is treated as a noisy reading of one hidden trend, estimated each day with a Kalman filter (Kalman, 1960; Harvey, 1989, *Forecasting, Structural Time Series Models and the Kalman Filter*). It weights signals by their noise and allows for shared errors, which majority voting cannot.
  - Conditions: one pre-declared run, counted in the budget; parameters estimated on past data only, refitted on an expanding window; it must beat the agreement rule out of sample.
  - If the agreement rule fails claim 1, this is not a rescue. It becomes a new hypothesis for a later project, written down before testing.
  - A neural network (for example a temporal transformer) is only considered after the state-space model, and needs more data than daily bars on two coins.
- **A wider signal pool (volume, funding rates, on-chain activity, attention):** only if the correlation pre-check leaves a family with one signal. Each new signal needs a written source first, and should draw on information other than the closing price, so that its errors differ from the existing signals' (Dietterich's diversity condition).
- **Hidden Markov model as the regime rule:** only if claim 2 passes with the simple rules, tested as one pre-declared change against them.
- **Trend and volatility combined:** only if each passes on its own.
- **Vol-forecast position sizing:** only after claim 3, as one pre-declared change.
- **Funding-rate and intraday data:** only when a passed claim needs them.
- **Other regime definitions:** not added after results are seen.
- **A web dashboard** showing the research (claims, results, run log) and, once live, positions, trades and the kill rule: only after claim 3 and the frozen test pass, as part of the monitoring requirement in section 11.

---

## 10. Open questions

- **To confirm with the team lead:** that the fund trades crypto through Alpaca, at tier 1, with no shorting. Current assumption from my own understanding (17/11/26). **[DECIDE]** date asked and the answer.
- Did the April–May V1 runs include 2026 data? If so, early 2026 is not unseen.
- Which V1 version was carried into V2? The October reruns (Sharpe 0.533, 425 orders) match the last May run (0.526, 425 orders), not the 0.94 run. To confirm in the code.
- What changed between the V1 runs? Recoverable from QuantConnect's stored code.
- What stop rule applies before deployment (for example a drawdown limit)? It is set from the results, in writing, before paper trading starts (rule 23).

---

## 11. Deployment requirements (worked on only if claim 3 and the frozen test pass)

Listed now so the standard is known in advance. None of this is built before then.

- **Execution:** the order type, when orders are placed relative to the signal, and a slippage assumption checked against real order-book data.
- **Shorts:** not applicable. The strategy is long or flat on Alpaca.
- **Capacity:** the largest position the market can absorb without moving the price against the trade.
- **Risk limits:** maximum position, maximum leverage and a drawdown stop, written before paper trading starts.
- **Monitoring:** what is tracked live, and the result that switches the strategy off.
- **Independent review:** someone else reruns the code and reproduces the numbers.
- **Live record:** a paper-trading period of a length fixed in advance.

---

## 12. Results

Results are added here in run order. Each entry names its run in `runs.csv`. Nothing above this section is changed because of a result.

### R01 — Regime labels and spell count (17/11/26, diagnostic)

- **Script:** `scripts/01_regimes.py`. Labels saved as `data/derived/regimes.parquet` (see `DATA.md`).
- **Sample:** BTC and ETH, 2018-01-01 to 2025-12-31. Every design day has a label (2,922 per coin).
- **Uses no forward returns,** so it cannot pass or fail a claim.

| Coin | State | Days | Spells | Spells ≥ 20 days | Median spell (days) | Meets minimum |
|---|---|---|---|---|---|---|
| BTC | Bull | 1,175 | 90 | 17 | 3 | Yes |
| BTC | Correction | 961 | 89 | 16 | 3 | Yes |
| BTC | Bear | 423 | 43 | 9 | 3 | Yes |
| BTC | Rebound | 363 | 43 | 6 | 2 | Yes |
| ETH | Bull | 976 | 68 | 15 | 4 | Yes |
| ETH | Correction | 776 | 73 | 14 | 4 | Yes |
| ETH | Bear | 655 | 51 | 9 | 4 | Yes |
| ETH | Rebound | 515 | 47 | 9 | 4 | Yes |

- **Every state meets the 5-spell minimum on both coins,** so no states are merged. Claim 2 is tested on all three predicted states. The weakest is BTC Rebound, with 6 long spells.
- **Most spells are very short:** the median is 2–4 days. The 30-day sign flips whenever the price is close to its level a month earlier, so a few long spells are surrounded by many brief ones.
- **Warning for claim 3, recorded before any returns are computed:** this is the first evidence on the persistence condition. A strategy that switches every time the label changes would trade very often and pay 0.25% each time.
- **The regime rule is not changed because of this.** Smoothing the labels or adding a minimum holding period now would be adjusting the spec after seeing data. If claim 3 fails on costs, this table is part of the explanation.

### R02 — Signals and family votes (18/11/26, diagnostic)

- **Script:** `scripts/02_signals.py`. Saved as `data/derived/signals.parquet` (see `DATA.md`).
- **Sample:** BTC and ETH, 2018-01-01 to 2025-12-31 (2,922 days per coin). Signals computed on 2017–2025 closes, then cut to 2018.
- **Uses no forward returns,** so it cannot pass or fail a claim.
- **Prediction written into the run before it ran:** momentum agreement above 0.9, reversion below 0.3 (from the consequences in section 6).

| Coin | Momentum agreement | Mean-reversion agreement |
|---|---|---|
| BTC | 1.00 | 0.21 |
| ETH | 1.00 | 0.21 |

(Agreement = share of days the family gives a reading under the majority rule.)

- **Both predictions held.**
- **Momentum agrees on every day,** confirming consequence 2 in section 6: three signals that always vote always produce a majority. In the momentum family, claim 1 is therefore a test of the majority **direction** against a single signal's direction, as already recorded.
- **Mean reversion agrees on about one day in five** (roughly 610 days per coin), confirming consequence 3. In that family the agreement rule does act as a filter, and there are enough days to test claims 1 and 2.
- **No missing scores in 2018–2025** for any signal, so the 2017 warm-up covers every lookback and there were no flat-RSI days.
- **Consequence 1 confirmed in code before this run:** the unit test `test_z_score_20_day_is_twice_bollinger` shows the 20-day z-score is exactly twice the Bollinger score on every day of a random price series. Real-data correlations come in phase 5.