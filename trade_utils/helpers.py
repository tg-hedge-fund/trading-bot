from api.portfolio import get_portfolio


def get_portfolio_holdings():
  HOLDINGS_LIST = []
  holdings = get_portfolio()
  for holding in holdings['holdings']:
      HOLDINGS_LIST.append(f"NSE-{holding['trading_symbol']}")
  return HOLDINGS_LIST

def on_data_received(meta):
    print("Data Received")