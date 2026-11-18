import pandas as pd
import numpy as np

from regime_consensus.config import RSI_PERIOD, RSI_LOWER, RSI_UPPER, RSI_MID
from regime_consensus.config import ROC_LOOKBACKS
from regime_consensus.config import MACD_FAST, MACD_SIGNAL, MACD_SLOW
from regime_consensus.config import BB_PERIOD, BB_WIDTH
from regime_consensus.config import Z_LOOKBACKS
from regime_consensus.config import FAMILIES

from regime_consensus.regime_modeling import _check_daily_index

from regime_consensus.agreement import family_vote

def sign_vote(score: pd.Series) -> pd.Series:
    return np.sign(score).replace(0, np.nan)

def rsi(close: pd.Series, period: int = RSI_PERIOD) -> pd.Series:
    diff = close.diff()

    gains = diff.clip(lower=0)
    avrg_gains = gains.ewm(alpha=1/period,adjust=False,min_periods=period).mean()

    losses = (-diff).clip(lower=0)
    avrg_losses = losses.ewm(alpha=1/period,adjust=False,min_periods=period).mean()

    rs = avrg_gains / avrg_losses
    return 100 -(100/(1+rs))

def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False, min_periods=span).mean()

def signal_rsi_50(close: pd.Series) -> pd.DataFrame:
    score = (rsi(close) - RSI_MID) / RSI_MID
    vote = sign_vote(score)
    return pd.DataFrame({"score":score, "vote":vote})

def signal_rate_of_change(
    close: pd.Series, lookbacks: tuple[int,...] = ROC_LOOKBACKS
) -> pd.DataFrame:
    returns = [close / close.shift(k) - 1 for k in lookbacks]
    score = pd.concat(returns, axis=1).mean(axis=1, skipna=False)
    vote = sign_vote(score)
    return pd.DataFrame({"score": score, "vote": vote})

def signal_macd(close: pd.Series) -> pd.DataFrame:
    macd = ema(close,MACD_FAST) - ema(close,MACD_SLOW)
    signal = ema(macd,MACD_SIGNAL)
    score = (macd - signal) / close
    vote = sign_vote(score)
    return pd.DataFrame({"score": score,"vote": vote})

def signal_rsi_extreme(close: pd.Series) -> pd.DataFrame:
   r = rsi(close)

   r_below = r < RSI_LOWER
   r_above = r > RSI_UPPER

   score = np.select(
        [r_below,r_above],
        [(RSI_LOWER - r) / RSI_LOWER,
         -(r - RSI_UPPER) / (100 - RSI_UPPER)],
         default=0.0
        )
   score = pd.Series(score, index=close.index).where(r.notna())
   vote = sign_vote(score)
   return pd.DataFrame({"score": score, "vote": vote})

def signal_bollinger_band(close: pd.Series, period: int = BB_PERIOD) -> pd.DataFrame:
    middle_line = close.rolling(period).mean()
    std_dev = close.rolling(period).std(ddof=0)

    score = -((close - middle_line) / (BB_WIDTH * std_dev))

    lower_band = close < middle_line - (BB_WIDTH * std_dev)
    upper_band = close > middle_line + (BB_WIDTH * std_dev)

    vote = pd.Series(np.select([lower_band,upper_band],[1,-1],default=np.nan),index=close.index)
    return pd.DataFrame({"score": score, "vote": vote})

def signal_z_score(close: pd.Series, lookbacks: tuple[int,...] = Z_LOOKBACKS) -> pd.DataFrame:
    z_scores = []
    for n in lookbacks:
        rolling_mean = close.rolling(window=n,min_periods=n).mean()
        rolling_std = close.rolling(window=n,min_periods=n).std(ddof=0)
        z_score = (close - rolling_mean) / rolling_std
        z_scores.append(z_score)
    z_table = pd.concat(z_scores, axis=1)
    score = -z_table.mean(axis=1, skipna=False)
    vote = sign_vote(score)
    return pd.DataFrame({"score": score, "vote": vote})

SIGNALS = {"rsi_50": signal_rsi_50, "rate_of_change": signal_rate_of_change, "macd": signal_macd, 
           "rsi_extreme": signal_rsi_extreme, "bollinger": signal_bollinger_band, "z_score":signal_z_score}

def build_signals(prices: pd.DataFrame) -> pd.DataFrame:
    frames = []

    for coin, coin_prices in prices.groupby("coin"):
        close = coin_prices.set_index("date")["close"].sort_index()

        _check_daily_index(close)

        signal_tables = []                              # one list per coin
        for name, function in SIGNALS.items():
            result = function(close)                    # a table with "score" and "vote"
            result = result.add_prefix(f"{name}_")      # -> "rsi_50_score", "rsi_50_vote"
            signal_tables.append(result)

        table = pd.concat(signal_tables, axis=1)        # 12 columns side by side, one row per date

        for family, names in FAMILIES.items():
            table[f"{family}_vote"] = family_vote(table[[f"{n}_vote" for n in names]])

        table = table.reset_index()
        table.insert(0,"coin", coin)
        frames.append(table)

    return pd.concat(frames, ignore_index=True)