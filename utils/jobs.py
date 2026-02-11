import logging
from threading import Thread

import schedule

from trade_utils.save_instruments import save_instrument_eq, save_instrument_idx
from utils.token_generator import generate_token


def run_job_every_mon_fri(time, fn, *args):
    schedule.every().monday.at(time).do(fn, *args)
    schedule.every().tuesday.at(time).do(fn, *args)
    schedule.every().wednesday.at(time).do(fn, *args)
    schedule.every().thursday.at(time).do(fn, *args)
    schedule.every().friday.at(time).do(fn, *args)

def scheduled_jobs_instrument(run_arg):
    if (run_arg == "EQ"):
        save_instrument_eq_thread = Thread(target=save_instrument_eq)
        save_instrument_eq_thread.daemon = True

        if save_instrument_eq_thread.daemon:
            logging.info("Starting save_instrument_eq thread")
            save_instrument_eq_thread.start()
    elif (run_arg == "IDX"):
        save_instrument_idx_thread = Thread(target=save_instrument_idx)
        save_instrument_idx_thread.daemon = True

        if save_instrument_idx_thread.daemon:
            logging.info("Starting save_instrument_idx thread")
            save_instrument_idx_thread.start()



def generate_token_every_morning_mtof():
    generate_token()
