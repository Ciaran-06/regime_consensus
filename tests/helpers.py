import numpy as np
import pandas as pd


def daily(values):
    """A made-up price series with one row per day."""
    return pd.Series(values, index=pd.date_range("2018-01-01", periods=len(values)), dtype=float)


def calm(n=30):
    """A quiet price wiggling between 100 and 101."""
    return [100 + (i % 2) for i in range(n)]