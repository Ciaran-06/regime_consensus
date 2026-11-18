import numpy as np
import pandas as pd

from regime_consensus.signals import rsi, signal_rsi_50,signal_rate_of_change,signal_macd

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

def test_roc_hand_calculated():
    result = signal_rate_of_change(daily([100, 110, 99, 121]), lookbacks=(1, 2))
    assert result["score"].iloc[:2].isna().all()
    assert np.isclose(result["score"].iloc[2], -0.055)
    assert np.isclose(result["score"].iloc[3], (121 / 99 - 1 + 0.10) / 2)
    assert list(result["vote"].iloc[2:]) == [-1, 1]


def test_roc_rising_votes_up():
    result = signal_rate_of_change(daily(range(1, 41)))
    assert (result["vote"].dropna() == 1).all()


def test_roc_falling_votes_down():
    result = signal_rate_of_change(daily(range(40, 0, -1)))
    assert (result["vote"].dropna() == -1).all()


def test_roc_nan_until_longest_lookback():
    result = signal_rate_of_change(daily(range(1, 41)))
    assert result.iloc[:20].isna().all().all()
    assert result.iloc[20:].notna().all().all()


def test_roc_flat_price_has_no_vote():
    result = signal_rate_of_change(daily([100.0] * 30))
    assert (result["score"].dropna() == 0).all()
    assert result["vote"].isna().all()


def test_roc_no_lookahead():
    prices = daily(np.linspace(100, 140, 60) + np.sin(np.arange(60)) * 3)
    changed = prices.copy()
    changed.iloc[40:] = changed.iloc[40:] * 2
    pd.testing.assert_frame_equal(
        signal_rate_of_change(prices).iloc[:40], signal_rate_of_change(changed).iloc[:40]
    )

def test_macd_accelerating_rise_votes_up():
    days = np.arange(80)
    result = signal_macd(daily(100 + days ** 2))
    assert (result["vote"].dropna() == 1).all()


def test_macd_accelerating_fall_votes_down():
    days = np.arange(80)
    result = signal_macd(daily(10_000 - days ** 2))
    assert (result["vote"].dropna() == -1).all()


def test_macd_nan_until_day_34():
    result = signal_macd(daily(100 + np.arange(80) ** 2))
    assert result.iloc[:33].isna().all().all()
    assert result.iloc[33:].notna().all().all()


def test_macd_no_lookahead():
    prices = daily(np.linspace(100, 140, 80) + np.sin(np.arange(80)) * 3)
    changed = prices.copy()
    changed.iloc[60:] = changed.iloc[60:] * 2
    pd.testing.assert_frame_equal(signal_macd(prices).iloc[:60], signal_macd(changed).iloc[:60])