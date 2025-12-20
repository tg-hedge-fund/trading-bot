from api.historical_data import get_historical_data
from api.portfolio import get_portfolio

from utils.app_config import extract_groww_keys
from trade_utils.ta_indicators import calculate_ema, calculate_sma
from utils.token_generator import generate_token, get_access_token
from trade_utils.save_instruments import save_instrument_eq, save_instrument_idx

import pandas as pd

ACCESS_TOKEN, GROWW, FEED = get_access_token()

save_instrument_eq()
