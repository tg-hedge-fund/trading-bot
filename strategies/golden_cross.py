# this strategy is for short ema crossing over the longer ema line
# will be applied on nifty 500 trades (because of volume concerns)
# time frame: 1hour or 1day
# paper trading mode please
# golden cross is lagging indicator, move has already happened before this indicator spots it

from trade_utils.ta_indicators import calculate_ema, calculate_ema_crossover
from utils.discord_bot import DiscordClient

ema_50 = []
ema_100 = []

# fetch live data every second from the groww api
data = []

ema_50 = calculate_ema(50, data)
ema_100 = calculate_ema(100, data)

crossover_50_100 = calculate_ema_crossover(ema_50, ema_100)

for i in range(len(crossover_50_100)):
  if crossover_50_100[i][0] > crossover_50_100[i][1]:
    #send message via discord bot that 50 ema has crossed 100 ema
    message_sent = 
  else:
    #send message via discord bot that 50 ema has broken below 100 ema
    pass
