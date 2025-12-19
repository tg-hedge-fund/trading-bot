from utils.token_generator import get_access_token

ACCESS_TOKEN, GROWW, FEED = get_access_token()

def get_portfolio():
    holdings_response = GROWW.get_holdings_for_user(timeout=5)
    return holdings_response

