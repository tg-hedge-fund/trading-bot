from utils.token_generator import get_access_token

ACCESS_TOKEN, GROWW, FEED = get_access_token()

def stream_live_data_by_quote(exchange, segment, trading_symbol):
  live_data_by_quote_response = GROWW.get_quote(
      exchange=exchange,
      segment=segment,
      trading_symbol=trading_symbol
  )

  return live_data_by_quote_response
