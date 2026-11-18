import pandas as pd
from regime_consensus.config import CORR_THRESHOLD,MOMENTUM_PRIORITY,REVERSION_PRIORITY

def select_signals(correlations: dict[str, pd.DataFrame],priority: list[str],
                    threshold: float = CORR_THRESHOLD,) -> list[str]:
    for coin, table in correlations.items():
        missing = [s for s in priority if s not in table.index or s not in table.columns]
        if missing:
            raise ValueError(f"{coin} correlation table has no row or column for {missing}")
        
    kept_signals = []
    for signal in priority:                          # go down the order
        too_similar = False
        for table in correlations.values():          # every coin's table
            for other in kept_signals:                       # every signal kept so far
                if table.loc[signal, other] > threshold:
                    too_similar = True
        if not too_similar:
            kept_signals.append(signal)
    return kept_signals