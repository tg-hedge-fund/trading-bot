from utils.discord_bot import send_message_via_discord_bot
from utils.token_generator import get_access_token

ACCESS_TOKEN, GROWW, FEED = get_access_token()

def refresh_groww_credentials():
    global ACCESS_TOKEN, GROWW, FEED
    try:
        ACCESS_TOKEN, GROWW, FEED = get_access_token()
    except Exception as e:
        send_message_via_discord_bot(f"Error refreshing GROWW credentials: {e}")
        raise

# https://groww.in/trade-api/docs/python-sdk/backtesting#get-historical-candle-data
def get_historical_data(start_time, end_time, groww_symbol, exchange, segment, candle_interval):
    try:
        historical_data_response = GROWW.get_historical_candles(
            groww_symbol=groww_symbol,
            exchange=exchange,
            segment=segment,
            start_time=start_time,
            end_time=end_time,
            candle_interval=candle_interval
        )

        return historical_data_response
    except Exception as e:
        send_message_via_discord_bot(f"Error in fetching historical data from GROWW API: {e}")
        RuntimeError(f"Error in fetching historical data from GROWW API: {e}")
  # You can also use expiries and contracts API to get historical data of FNO instruments
  
  # jan2024_nifty_expiries = groww.get_expiries(
  #     exchange=groww.EXCHANGE_NSE,
  #     underlying_symbol="NIFTY",
  #     year=2024,
  #     month=1
  # )

def stream_live_data_by_quote(exchange, segment, trading_symbol):
    try:
        live_data_by_quote_response = GROWW.get_quote(
            exchange=exchange,
            segment=segment,
            trading_symbol=trading_symbol
        )

        return live_data_by_quote_response
    except Exception as e:
        send_message_via_discord_bot(f"Error in fetching live quote from GROWW API: {e}")
        RuntimeError(f"Error in fetching live quote from GROWW API: {e}")


def get_portfolio():
    try:
        holdings_response = GROWW.get_holdings_for_user(timeout=5)
        return holdings_response
    except Exception as e:
        send_message_via_discord_bot(f"Error in fetching portfolio from GROWW API: {e}")
        RuntimeError(f"Error in fetching portfolio from GROWW API: {e}")
