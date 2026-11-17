import numpy as np
import pandas as pd

from regime_consensus.signals import rsi, signal_rsi_50

def daily(values):
    """A made-up price series with one row per day."""
    return pd.Series(values, index=pd.date_range("2018-01-01", periods=len(values)), dtype=float)


def test_only_rising_gives_100():
    result = rsi(daily(range(1, 41)))
    assert (result.dropna() == 100).all()


def test_only_falling_gives_0():
    result = rsi(daily(range(40, 0, -1)))
    assert (result.dropna() == 0).all()


def test_alternating_settles_near_50():
    result = rsi(daily([100 + (i % 2) for i in range(200)]))
    assert 45 < result.iloc[-1] < 55


def test_nan_until_enough_history():
    result = rsi(daily(range(1, 41)))
    assert result.iloc[:14].isna().all()
    assert result.iloc[14:].notna().all()


def test_flat_price_gives_nan():
    result = rsi(daily([100.0] * 30))
    assert result.isna().all()


def test_no_lookahead():
    prices = daily(np.linspace(100, 140, 60) + np.sin(np.arange(60)) * 3)
    changed = prices.copy()
    changed.iloc[40:] = changed.iloc[40:] * 2          # change only the future
    pd.testing.assert_series_equal(rsi(prices).iloc[:40], rsi(changed).iloc[:40])


def test_rsi_50_rising_votes_up():
    result = signal_rsi_50(daily(range(1, 41)))
    assert (result["vote"].dropna() == 1).all()
    assert result["vote"].notna().sum() == 40 - 14      # every day after the warm-up votes


def test_rsi_50_falling_votes_down():
    result = signal_rsi_50(daily(range(40, 0, -1)))
    assert (result["vote"].dropna() == -1).all()


def test_rsi_50_score_between_minus_one_and_one():
    prices = daily(100 + np.cumsum(np.random.default_rng(0).normal(0, 1, 300)))
    score = signal_rsi_50(prices)["score"].dropna()
    assert score.between(-1, 1).all()


def test_rsi_50_warm_up_has_no_score_or_vote():
    result = signal_rsi_50(daily(range(1, 41)))
    assert result.iloc[:14].isna().all().all()


def test_rsi_50_no_lookahead():
    prices = daily(np.linspace(100, 140, 60) + np.sin(np.arange(60)) * 3)
    changed = prices.copy()
    changed.iloc[40:] = changed.iloc[40:] * 2           # change only the future
    pd.testing.assert_frame_equal(signal_rsi_50(prices).iloc[:40], signal_rsi_50(changed).iloc[:40])