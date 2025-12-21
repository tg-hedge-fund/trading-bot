from threading import Thread
import schedule
import time
import logging

from api.historical_data import get_historical_data
from api.portfolio import get_portfolio
from utils.app_config import extract_groww_keys
from trade_utils.ta_indicators import calculate_ema, calculate_sma
from utils.token_generator import generate_token, get_access_token
from trade_utils.save_instruments import save_instrument_eq, save_instrument_idx

import pandas as pd

ACCESS_TOKEN, GROWW, FEED = get_access_token()

def scheduled_jobs():
    # save_instrument_eq()
    save_instrument_eq_thread = Thread(target=save_instrument_eq)
    save_instrument_eq_thread.daemon = True

    if save_instrument_eq_thread.daemon == True:
        logging.info("Starting save_instrument_eq thread")
        print("Starting save_instrument_eq thread")
        save_instrument_eq_thread.start()

if __name__ == "__main__":
    schedule.every().monday.at("09:16").do(scheduled_jobs)
    schedule.every().tuesday.at("09:16").do(scheduled_jobs)
    schedule.every().wednesday.at("09:16").do(scheduled_jobs)
    schedule.every().thursday.at("09:16").do(scheduled_jobs)
    schedule.every().friday.at("09:16").do(scheduled_jobs)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
