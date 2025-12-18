from api.historical_data import get_historical_data
from api.portfolio import get_portfolio

from utils.app_config import extract_groww_keys
from trade_utils.ta_indicators import calculate_ema, calculate_sma
from utils.token_generator import generate_token, get_access_token

import pandas as pd

API_AUTH_TOKEN, GROWW, FEED = get_access_token()

all_equities = pd.read_csv("instrument-eq.csv")
instrument_exchange_token = all_equities["exchange_token"].tolist()
eq_symbols = all_equities["groww_symbol"].tolist()

# list of instruments to subscribe to:
INSTRUMENT_LIST = []


# input: start_time, end_time, groww_symbol, exchange, segment, candle_interval
# output: timestamp (epoch sec), OHLC, volume

# for holding in HOLDINGS_LIST:
#     print(f"Fetching historical data for {holding}")


# historical_data = get_historical_data(
#         "2025-01-01 09:15:00",
#         "2025-11-28 15:15:00",
#         "NSE-SJVN",
#         GROWW.EXCHANGE_NSE,
#         GROWW.SEGMENT_CASH,
#         GROWW.CANDLE_INTERVAL_DAY,
#     )
  
# # print(historical_data)

# ema_50 = calculate_ema(50, historical_data['candles'])
# ema_100 = calculate_ema(100, historical_data['candles'])

