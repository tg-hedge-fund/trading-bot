# this strategy is for short ema crossing over the longer ema line
# will be applied on nifty 500 trades (because of volume concerns)
# time frame: 1hour or 1day
# paper trading mode please
# golden cross is lagging indicator, move has already happened before this indicator spots it

from trade_utils.ta_indicators import calculate_ema_crossover

ema_50 = []
ema_200 = []

calculate_ema_crossover(ema_50, ema_200)
