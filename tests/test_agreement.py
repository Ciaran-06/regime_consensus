import numpy as np
import pandas as pd
import pytest

from regime_consensus.agreement import count_votes, family_vote, agreement_rate

NAN = np.nan


def example_votes():
    """The six-row table: one row per case."""
    return pd.DataFrame(
        [[1, 1, 1], [1, 1, -1], [-1, -1, NAN], [1, -1, NAN], [NAN, NAN, 1], [NAN, NAN, NAN]],
        columns=["a", "b", "c"],
        index=pd.date_range("2018-01-01", periods=6),
    )


def test_count_votes_counts_each_row():
    votes = example_votes()
    assert list(count_votes(votes, "UP")) == [3, 2, 0, 1, 1, 0]
    assert list(count_votes(votes, "DOWN")) == [0, 1, 2, 1, 0, 0]


def test_count_votes_rejects_unknown_direction():
    with pytest.raises(ValueError):
        count_votes(example_votes(), "SIDEWAYS")


def test_family_vote_majority_rule():
    result = family_vote(example_votes())
    expected = pd.Series([1, 1, -1, NAN, NAN, NAN], index=example_votes().index)
    pd.testing.assert_series_equal(result, expected, check_dtype=False)


def test_family_vote_two_signals_need_both():
    # after the pre-check drops a signal, both remaining must agree
    votes = pd.DataFrame({"a": [1, 1, -1], "b": [1, -1, NAN]})
    assert list(family_vote(votes).fillna(0)) == [1, 0, 0]


def test_family_vote_rejects_min_agree_of_half_or_less():
    with pytest.raises(ValueError):
        family_vote(example_votes(), min_agree=1)
    with pytest.raises(ValueError):
        four = pd.DataFrame({"a": [1], "b": [1], "c": [1], "d": [1]})
        family_vote(four, min_agree=2)

def test_agreement_rate():
    assert agreement_rate(pd.Series([1, NAN, -1, NAN])) == 0.5
    assert agreement_rate(pd.Series([1, 1, -1])) == 1.0
    assert agreement_rate(pd.Series([NAN, NAN, NAN])) == 0.0