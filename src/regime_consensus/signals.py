import pandas as pd
import numpy as np

from regime_consensus.config import RSI_PERIOD, RSI_LOWER, RSI_UPPER, RSI_MID
from regime_consensus.config import ROC_LOOKBACKS
from regime_consensus.config import MACD_FAST, MACD_SIGNAL, MACD_SLOW
from regime_consensus.config import BB_PERIOD, BB_WIDTH
from regime_consensus.config import Z_LOOKBACKS

def rsi(close: pd.Series, period: int = RSI_PERIOD) -> pd.Series:
    diff = close.diff()

    gains = diff.clip(lower=0)
    avrg_gains = gains.ewm(alpha=1/period,adjust=False,min_periods=period).mean()

    losses = (-diff).clip(lower=0)
    avrg_losses = losses.ewm(alpha=1/period,adjust=False,min_periods=period).mean()

    rs = avrg_gains / avrg_losses
    return 100 -(100/(1+rs))

def signal_rsi_50(close: pd.Series) -> pd.DataFrame:
    score = (rsi(close) - RSI_MID) / RSI_MID
    vote = np.sign(score)
    vote = vote.where(vote != 0)
    return pd.DataFrame({"score":score, "vote":vote})