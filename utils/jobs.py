from concurrent.futures import ThreadPoolExecutor

import schedule

from trade_utils.save_instruments import save_instrument_eq, save_instrument_idx
from utils.discord_bot import send_message_via_discord_bot
from utils.token_generator import generate_token
from utils.utils import logger

_executor = ThreadPoolExecutor(max_workers=2)

def submit_job(fn, *args):
    try:
          _executor.submit(fn, *args)
    except Exception as e:
          logger.error(f"Failed to submit job to executor {fn.__name__}: {e}", exc_info=True)

def run_job_every_mon_fri(time, fn, *args):
    schedule.every().monday.at(time).do(fn, *args)
    schedule.every().tuesday.at(time).do(fn, *args)
    schedule.every().wednesday.at(time).do(fn, *args)
    schedule.every().thursday.at(time).do(fn, *args)
    schedule.every().friday.at(time).do(fn, *args)

def run_job_everyday(time, fn, *args):
    schedule.every().day.at(time).do(fn, *args)

def scheduled_jobs_instrument(run_arg):
    logger.info("Running save instrument job...")
    if (run_arg == "EQ"):
        submit_job(save_instrument_eq)
    elif (run_arg == "IDX"):
        submit_job(save_instrument_idx)

def generate_token_every_morning():
    send_message_via_discord_bot("Generating Token...")
    generate_token()

def shutdown_job_executor(wait=True):
    logger.info("Shutting down scheduled jobs executor...")
    _executor.shutdown(wait=wait)
