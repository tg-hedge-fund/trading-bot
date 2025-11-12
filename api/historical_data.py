# https://groww.in/trade-api/docs/python-sdk/backtesting#get-historical-candle-data

from utils.token_generator import get_access_token

API_AUTH_TOKEN, GROWW = get_access_token()

def get_historical_data(start_time, end_time, groww_symbol, exchange, segment, candle_interval):
  historical_data_response = GROWW.get_historical_candles(
      groww_symbol=groww_symbol,
      exchange=exchange,
      segment=segment,
      start_time=start_time,
      end_time=end_time,
      candle_interval=candle_interval
  )

  return historical_data_response

# You can also use expiries and contracts API to get historical data of FNO instruments

# jan2024_nifty_expiries = groww.get_expiries(
#     exchange=groww.EXCHANGE_NSE,
#     underlying_symbol="NIFTY",
#     year=2024,
#     month=1
# )
