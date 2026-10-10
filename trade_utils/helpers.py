from api_utils.fyers_api_handlers import get_portfolio


def get_portfolio_holdings():
  HOLDINGS_LIST = []
  holdings = get_portfolio()
  for holding in holdings['holdings']:
      HOLDINGS_LIST.append(holding['symbol'])
  return HOLDINGS_LIST
