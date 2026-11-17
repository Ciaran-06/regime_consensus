import pandas as pd

from regime_consensus import DESIGN_COINS
from regime_consensus.config import DESIGN_END ,DESIGN_START
from regime_consensus.io import load_clean, save_derived
from regime_consensus.regime_modeling import label_regimes, find_spells, spell_summary

coins = load_clean(DESIGN_COINS,columns=["close","date"], end=DESIGN_END)

labeled_coins = label_regimes(coins)
labeled_coins = labeled_coins[labeled_coins["date"] >= pd.Timestamp(DESIGN_START)]
save_derived(labeled_coins, "regimes")

spells = find_spells(labeled_coins)
print(spell_summary(spells))
