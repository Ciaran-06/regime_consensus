import numpy as np
import pandas as pd

from helpers import daily
from regime_consensus.regime_modeling import label_volatility


def test_volatility_turns_high_when_markets_get_wild():
    rng = np.random.default_rng(0)
    calm_returns = rng.normal(0, 0.005, 500)
    wild_returns = rng.normal(0, 0.05, 60)
    close = daily(100 * np.exp(np.cumsum(np.concatenate([calm_returns, wild_returns]))))
    labels = label_volatility(close)
    assert (labels.iloc[-30:] == "HIGH").all()


def test_volatility_constant_price_is_low():
    # every return is exactly 0, so volatility is exactly 0 and never above its median
    close = daily([100.0] * 500)
    assert (label_volatility(close).dropna() == "LOW").all()


def test_volatility_first_label_on_day_396():
    close = daily(100 * np.exp(np.cumsum(np.random.default_rng(1).normal(0, 0.02, 500))))
    labels = label_volatility(close)
    assert labels.iloc[:395].isna().all()
    assert labels.iloc[395:].notna().all()


def test_volatility_no_lookahead():
    close = daily(100 * np.exp(np.cumsum(np.random.default_rng(2).normal(0, 0.02, 500))))
    changed = close.copy()
    changed.iloc[450:] = changed.iloc[450:] * 3
    pd.testing.assert_series_equal(label_volatility(close).iloc[:450], label_volatility(changed).iloc[:450])