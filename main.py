
from api.historical_data import get_historical_data
from utils.token_generator import get_access_token

API_AUTH_TOKEN, GROWW = get_access_token()

# input: start_time, end_time, groww_symbol, exchange, segment, candle_interval
# output: timestamp (epoch sec), OHLC, volume
historical_data = get_historical_data(
    "2025-10-24 09:15:00",
    "2025-10-31 15:15:00",
    "NSE-NETWEB",
    GROWW.EXCHANGE_NSE,
    GROWW.SEGMENT_CASH,
    GROWW.CANDLE_INTERVAL_DAY,
)

