# BACKTESTING.md | regime_consensus | Rules for every test in this project

Last updated 16/11/26.

These are this project's own rules, written in my own words. Rules tagged **[AHM]** apply a principle from the paper below to this project. Rules tagged **[Project]** come from decisions made for this project.

**Source:** Arnott, R., Harvey, C. R., & Markowitz, H. (2019). A Backtesting Protocol in the Era of Machine Learning. *Journal of Financial Data Science*, 1(1), 64–74. https://doi.org/10.3905/jfds.2019.1.064 (free version: https://papers.ssrn.com/abstract=3275654)

A rule is only changed in writing, with a date and a reason, and never after seeing a result it affects.

---

## A. Before any data is loaded

1. **Write the hypothesis first, with its reason.** State who is on the losing side of the trade and why they keep losing. **[AHM]**
   *Why:* a story written after seeing the data will always fit the data.

2. **Give every rule and parameter a source before testing it:** a paper, a first-principles argument, or the words "convention, no academic support". **[Project]**
   *Why:* a value with no source is a value that was tuned. Looking for a paper to justify a choice already made is overfitting by citation.

3. **Fix the sample, the data split and the trading costs in advance.** **[AHM]**
   *Why:* each of these can be adjusted until a result appears.

4. **Write each kill test before running it:** metric, comparison, sample and a numeric threshold, plus the decision that follows a pass or a fail. **[Project]**
   *Why:* a test with a missing part can be argued either way afterwards, so it cannot fail.

5. **Name one confirmatory run per claim in advance. Every other run is diagnostic and cannot pass a claim.** **[AHM]**
   *Why:* about one in twenty strategies with no edge clears $t = 2$ by luck. Twenty attempts at one threshold would be expected to produce a false pass.

---

## B. Data

6. **Never edit raw data. Document every cleaning step and transformation, and decide any outlier rule before modelling.** **[AHM]**
   *Why:* undocumented cleaning is a hidden way of choosing the result.

7. **Signals and regime labels use only information available on that day.** No thresholds set from the whole sample, and no labels that use later data. **[Project]**
   *Why:* anything that sees the future will look better in a backtest than it can in trading.

8. **A trade never fills at the price that produced its signal.** **[Project]**
   *Why:* you cannot trade at a close you needed in order to decide.

---

## C. While testing

9. **Log every run in `runs.csv`:** date, what changed and the result, including failures, duplicates and bugs. **[AHM]**
   *Why:* the number of attempts decides how much any single result is worth.

10. **One change per run.** **[Project]**
    *Why:* with two changes you cannot tell which one caused the difference.

11. **Stay inside the run budget of 20.** If it is used up, stop and write up what exists. **[Project]**
    *Why:* an unlimited budget is a search.

12. **Never tune a parameter on the design period.** Where a value has to be chosen, average over a range. **[Project]**
    *Why:* the design period has already been seen, so anything fitted to it is fitted to known history.

13. **Prefer the simplest version.** A more complex model is adopted only if it beats the simpler one by a margin that matters after costs. **[AHM]**
    *Why:* complexity always fits the past better and usually disappoints afterwards.

14. **Always include trading costs, and report at more than one fee level.** **[AHM]**
    *Why:* this strategy's earlier results halved between a 0.1% and a 0.6% fee.

15. **Compare against honest benchmarks:** holding the coin at the same risk, the single-signal version, and random entries with the same exposure. **[Project]**
    *Why:* in a market that rose, almost anything long-biased looks skilled.

---

## D. Out-of-sample evidence

16. **Open the frozen test set once, at the end. If it fails, the strategy is not adjusted and retested.** **[AHM]**
    *Why:* changing a model after an out-of-sample failure turns that data into in-sample data.

17. **Treat the unseen coins as supporting evidence only.** **[AHM]**
    *Why:* other coins move with BTC, so they are not an independent test.

18. **Only live or paper trading is truly out of sample. Paper trade before any money is committed.** **[AHM]**
    *Why:* every historical test is run by someone who already knows roughly how history went.

---

## E. Reporting

19. **Report every claim tested, pass or fail, and the total number of runs including the exploratory phase.** **[AHM]**
    *Why:* reporting only the winners hides the search that found them.

20. **State each result with its uncertainty,** and write "not significant" when it is not. **[Project]**
    *Why:* a Sharpe ratio from eight years of data carries an error of roughly ±0.35.

21. **State the limits of every paper cited:** which market, which period, which frequency. **[Project]**
    *Why:* most evidence is on monthly equity data, and carrying it to daily crypto is an assumption.

22. **A failed test is a result. Most ideas are expected to fail.** **[AHM]**
    *Why:* treating failure as a problem to fix is what turns research into a search for a good backtest.

---

## F. Before and after deployment

23. **No deployment without all of:** the claims passed, the frozen test passed, a paper-trading period, a written stop rule (for example a drawdown limit) fixed in advance, and a review by someone else. **[Project]**
    *Why:* this is other people's money, and a backtest alone is not evidence that it is safe.

24. **Do not adjust a live model in response to recent results.** Any change goes through this whole process again. **[AHM]**
    *Why:* adjusting to the last few months is overfitting in real time.

25. **Assume the edge fades, and watch for it.** **[AHM]**
    *Why:* effects weaken once they are known and traded, and crypto momentum has been public for years.