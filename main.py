from api.historical_data import get_historical_data
from api.portfolio import get_portfolio

from utils.ta_indicators import calculate_ema, calculate_sma
from utils.token_generator import get_access_token


API_AUTH_TOKEN, GROWW = get_access_token()

HOLDINGS_LIST = []

holdings = get_portfolio()

for holding in holdings['holdings']:
    HOLDINGS_LIST.append(f"NSE-{holding['trading_symbol']}")

print(HOLDINGS_LIST)

# input: start_time, end_time, groww_symbol, exchange, segment, candle_interval
# output: timestamp (epoch sec), OHLC, volume

# for holding in HOLDINGS_LIST:
#     print(f"Fetching historical data for {holding}")


historical_data = get_historical_data(
        "2025-01-01 09:15:00",
        "2025-06-30 15:15:00",
        "NSE-SJVN",
        GROWW.EXCHANGE_NSE,
        GROWW.SEGMENT_CASH,
        GROWW.CANDLE_INTERVAL_DAY,
    )
  
# print(historical_data)

ema_50 = calculate_ema(50, historical_data['candles'])
ema_100 = calculate_ema(100, historical_data['candles'])
# print(len(historical_data['candles']))
# print(ema_50)
# print(ema_100)

starting_point = len(ema_50) - len(ema_100)

ema_crossover = [(ema_50[starting_point + i], ema_100[i]) for i in range(len(ema_100))]

for i in range(len(ema_crossover)):
    if ema_crossover[i][0] > ema_crossover[i][1]:
        print("50 EMA is above 100 EMA")
    else:
        print("100 EMA is above 50 EMA")
# op = calculate_sma(3, [1,2,3,7])
# print(op)

# output = calculate_ema(3, [1,2,3,4,5,6,7])
# print(output)
