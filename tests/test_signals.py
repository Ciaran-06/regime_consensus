import numpy as np
import pandas as pd
import pytest

from regime_consensus.signals import rsi, signal_rsi_50,signal_rate_of_change,signal_macd
from regime_consensus.signals import signal_rsi_extreme, signal_bollinger_band, signal_z_score

from regime_consensus.config import MOMENTUM_SIGNALS, REVERSION_SIGNALS
from regime_consensus.signals import SIGNALS, build_signals, signal_rsi_50, signal_z_score

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

def test_rsi_extreme_falling_votes_up():
    result = signal_rsi_extreme(daily(range(40, 0, -1)))
    assert (result["vote"].dropna() == 1).all()           # oversold: expect a bounce
    assert (result["score"].dropna() == 1).all()          # RSI 0 is the very end of the scale


def test_rsi_extreme_rising_votes_down():
    result = signal_rsi_extreme(daily(range(1, 41)))
    assert (result["vote"].dropna() == -1).all()
    assert (result["score"].dropna() == -1).all()


def test_rsi_extreme_middle_has_zero_score_and_no_vote():
    result = signal_rsi_extreme(daily([100 + (i % 2) for i in range(200)]))
    assert (result["score"].dropna() == 0).all()
    assert result["vote"].isna().all()


def test_rsi_extreme_warm_up_is_nan_not_zero():
    result = signal_rsi_extreme(daily(range(1, 41)))
    assert result.iloc[:14].isna().all().all()


def test_rsi_extreme_score_between_minus_one_and_one():
    prices = daily(100 + np.cumsum(np.random.default_rng(0).normal(0, 1, 300)))
    assert signal_rsi_extreme(prices)["score"].dropna().between(-1, 1).all()


def test_rsi_extreme_no_lookahead():
    prices = daily(np.linspace(100, 140, 60) + np.sin(np.arange(60)) * 3)
    changed = prices.copy()
    changed.iloc[40:] = changed.iloc[40:] * 2
    pd.testing.assert_frame_equal(
        signal_rsi_extreme(prices).iloc[:40], signal_rsi_extreme(changed).iloc[:40]
    )

def calm(n=30):
    """A quiet price wiggling between 100 and 101."""
    return [100 + (i % 2) for i in range(n)]


def test_bollinger_hand_calculated():
    # window [1, 2, 3]: mean 2, population sd sqrt(2/3)
    result = signal_bollinger_band(daily([1, 2, 3, 4, 10]), period=3)
    assert result["score"].iloc[:2].isna().all()
    assert np.isclose(result["score"].iloc[2], -(3 - 2) / (2 * np.sqrt(2 / 3)))


def test_bollinger_sudden_drop_votes_up():
    result = signal_bollinger_band(daily(calm() + [90]))
    assert result["vote"].iloc[-1] == 1
    assert result["score"].iloc[-1] > 1


def test_bollinger_sudden_jump_votes_down():
    result = signal_bollinger_band(daily(calm() + [115]))
    assert result["vote"].iloc[-1] == -1
    assert result["score"].iloc[-1] < -1


def test_bollinger_inside_bands_has_no_vote():
    result = signal_bollinger_band(daily(calm(60)))
    assert result["vote"].isna().all()
    assert result["score"].iloc[19:].notna().all()


def test_bollinger_nan_until_full_window():
    result = signal_bollinger_band(daily(calm(40)))
    assert result["score"].iloc[:19].isna().all()
    assert result["score"].iloc[19:].notna().all()


def test_bollinger_no_lookahead():
    prices = daily(np.linspace(100, 140, 60) + np.sin(np.arange(60)) * 3)
    changed = prices.copy()
    changed.iloc[40:] = changed.iloc[40:] * 2
    pd.testing.assert_frame_equal(
        signal_bollinger_band(prices).iloc[:40], signal_bollinger_band(changed).iloc[:40]
    )

def test_z_score_hand_calculated():
    # the worked example: closes 10, 12, 11, 15 with lookbacks 2 and 3
    result = signal_z_score(daily([10, 12, 11, 15]), lookbacks=(2, 3))
    assert result["score"].iloc[:2].isna().all()
    assert np.isclose(result["score"].iloc[2], 0.5)
    z3 = (15 - np.mean([12, 11, 15])) / np.std([12, 11, 15])
    assert np.isclose(result["score"].iloc[3], -(1 + z3) / 2)
    assert list(result["vote"].iloc[2:]) == [1, -1]


def test_z_score_high_price_votes_down():
    result = signal_z_score(daily(calm(120) + [115]))
    assert result["vote"].iloc[-1] == -1


def test_z_score_low_price_votes_up():
    result = signal_z_score(daily(calm(120) + [90]))
    assert result["vote"].iloc[-1] == 1


def test_z_score_nan_until_longest_lookback():
    result = signal_z_score(daily(calm(150)))
    assert result["score"].iloc[:99].isna().all()
    assert result["score"].iloc[99:].notna().all()


def test_z_score_20_day_is_twice_bollinger():
    # NOTES.md section 6: Bollinger position is the 20-day z-score in disguise
    prices = daily(100 + np.cumsum(np.random.default_rng(1).normal(0, 1, 200)))
    z20 = signal_z_score(prices, lookbacks=(20,))["score"]
    bollinger = signal_bollinger_band(prices)["score"]
    pd.testing.assert_series_equal(z20, 2 * bollinger, check_names=False)


def test_z_score_no_lookahead():
    prices = daily(np.linspace(100, 140, 160) + np.sin(np.arange(160)) * 3)
    changed = prices.copy()
    changed.iloc[130:] = changed.iloc[130:] * 2
    pd.testing.assert_frame_equal(signal_z_score(prices).iloc[:130], signal_z_score(changed).iloc[:130])


def two_coin_prices(days=150):
    """Made-up prices for two coins on very different scales, one row per coin per day."""
    dates = pd.date_range("2017-01-01", periods=days)
    rows = []
    for coin, start, seed in [("AAA-USD", 100.0, 1), ("BBB-USD", 5.0, 2)]:
        steps = np.random.default_rng(seed).normal(0, 0.03, days)
        close = start * np.exp(np.cumsum(steps))
        rows.append(pd.DataFrame({"coin": coin, "date": dates, "close": close}))
    return pd.concat(rows, ignore_index=True)


def test_signal_names_match_config():
    assert set(MOMENTUM_SIGNALS) | set(REVERSION_SIGNALS) == set(SIGNALS)
    assert not set(MOMENTUM_SIGNALS) & set(REVERSION_SIGNALS)


def test_build_signals_columns():
    result = build_signals(two_coin_prices())
    expected = ["coin", "date"]
    for name in SIGNALS:
        expected += [f"{name}_score", f"{name}_vote"]
    expected += ["momentum_vote", "reversion_vote"]
    assert list(result.columns) == expected


def test_build_signals_one_row_per_coin_per_day():
    prices = two_coin_prices()
    result = build_signals(prices)
    assert len(result) == len(prices)
    assert not result.duplicated(["coin", "date"]).any()


def test_build_signals_each_coin_uses_only_its_own_prices():
    prices = two_coin_prices()
    result = build_signals(prices)
    for coin in ["AAA-USD", "BBB-USD"]:
        close = prices[prices["coin"] == coin].set_index("date")["close"]
        built = result[result["coin"] == coin].set_index("date")
        pd.testing.assert_series_equal(built["rsi_50_score"], signal_rsi_50(close)["score"], check_names=False)
        pd.testing.assert_series_equal(built["z_score_vote"], signal_z_score(close)["vote"], check_names=False)


def test_build_signals_rejects_a_missing_day():
    prices = two_coin_prices()
    gap = prices.drop(index=prices[prices["coin"] == "AAA-USD"].index[50])
    with pytest.raises(ValueError):
        build_signals(gap)


def test_build_signals_family_votes_only_plus_minus_one_or_nan():
    result = build_signals(two_coin_prices())
    for column in ["momentum_vote", "reversion_vote"]:
        assert set(result[column].dropna().unique()) <= {1, -1}