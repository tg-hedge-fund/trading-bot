from api_utils.groww_api_handlers import get_portfolio


def get_portfolio_holdings():
  HOLDINGS_LIST = []
  holdings = get_portfolio()
  for holding in holdings['holdings']:
      HOLDINGS_LIST.append(f"NSE-{holding['trading_symbol']}")
  return HOLDINGS_LIST
