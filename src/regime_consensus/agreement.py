import pandas as pd
import numpy as np
from typing import Literal
from regime_consensus.config import FAMILY_MIN_AGREE

Direction = Literal["UP", "DOWN"]
DIRECTION: dict[Direction, int] = {"UP": 1, "DOWN": -1}

def count_votes(votes: pd.DataFrame, direction: Direction) -> pd.Series:
    if direction not in DIRECTION:
        raise ValueError(f"Direction must be 'UP' or 'DOWN', got {direction!r}")
    return (votes == DIRECTION[direction]).sum(axis=1)

def family_vote(votes: pd.DataFrame, min_agree: int =FAMILY_MIN_AGREE) -> pd.Series:
    n_signals = len(votes.columns)
    if min_agree <= n_signals / 2:
        raise ValueError(f"min_agree must be more than half of the {n_signals} signals, got {min_agree}")

    ups = count_votes(votes,"UP")
    downs = count_votes(votes,"DOWN")

    enough_up = ups >= min_agree
    enough_down = downs >= min_agree

    family_vote = pd.Series(np.select([enough_up,enough_down], [1,-1],default=np.nan),index=votes.index)
    return family_vote

def agreement_rate(family_votes:pd.Series) -> float:
    return float(family_votes.notna().mean())
