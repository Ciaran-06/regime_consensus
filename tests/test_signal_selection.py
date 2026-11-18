import pandas as pd
import pytest

from regime_consensus.signal_selection import select_signals


def corr_table(pairs, names=("A", "B", "C")):
    """A correlation table from a few pair values: 1 on the diagonal, 0 for unlisted pairs."""
    table = pd.DataFrame(0.0, index=list(names), columns=list(names))
    for name in names:
        table.loc[name, name] = 1.0
    for (a, b), value in pairs.items():
        table.loc[a, b] = value
        table.loc[b, a] = value
    return table


def test_worked_example():
    correlations = {
        "BTC": corr_table({("A", "B"): 0.80, ("A", "C"): 0.30, ("B", "C"): 0.75}),
        "ETH": corr_table({("A", "B"): 0.60, ("A", "C"): 0.50, ("B", "C"): 0.40}),
    }
    assert select_signals(correlations, ["A", "B", "C"]) == ["A", "C"]


def test_nothing_above_threshold_keeps_all():
    correlations = {"BTC": corr_table({("A", "B"): 0.5}), "ETH": corr_table({("B", "C"): 0.6})}
    assert select_signals(correlations, ["A", "B", "C"]) == ["A", "B", "C"]


def test_one_pair_above_drops_the_lower_priority():
    correlations = {"BTC": corr_table({("B", "C"): 0.9}), "ETH": corr_table({("B", "C"): 0.9})}
    assert select_signals(correlations, ["A", "B", "C"]) == ["A", "B"]


def test_above_on_one_coin_only_still_drops():
    correlations = {"BTC": corr_table({("A", "B"): 0.71}), "ETH": corr_table({("A", "B"): 0.2})}
    assert select_signals(correlations, ["A", "B", "C"]) == ["A", "C"]


def test_exactly_threshold_is_kept():
    correlations = {"BTC": corr_table({("A", "B"): 0.7}), "ETH": corr_table({("A", "B"): 0.7})}
    assert select_signals(correlations, ["A", "B", "C"]) == ["A", "B", "C"]


def test_chain_keeps_the_far_end():
    correlations = {"BTC": corr_table({("A", "B"): 0.9, ("B", "C"): 0.9}), "ETH": corr_table({})}
    assert select_signals(correlations, ["A", "B", "C"]) == ["A", "C"]


def test_priority_order_decides_which_survives():
    correlations = {"BTC": corr_table({("A", "B"): 0.9}), "ETH": corr_table({})}
    assert select_signals(correlations, ["B", "A", "C"]) == ["B", "C"]


def test_unknown_signal_name_raises():
    with pytest.raises(ValueError):
        select_signals({"BTC": corr_table({})}, ["A", "B", "Z"])