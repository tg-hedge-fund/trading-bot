import schedule

from trade_utils.save_instruments import save_instrument_eq, save_instrument_idx
from utils.discord_bot import send_message_via_discord_bot
from utils.token_generator import generate_token
from utils.utils import logger


def run_job_every_mon_fri(time, fn, *args):
    schedule.every().monday.at(time).do(fn, *args)
    schedule.every().tuesday.at(time).do(fn, *args)
    schedule.every().wednesday.at(time).do(fn, *args)
    schedule.every().thursday.at(time).do(fn, *args)
    schedule.every().friday.at(time).do(fn, *args)

def scheduled_jobs_instrument(run_arg):
    if (run_arg == "EQ"):
        save_instrument_eq()
    elif (run_arg == "IDX"):
        save_instrument_idx()

def generate_token_every_morning_mtof():
    send_message_via_discord_bot("Generating Token...")
    generate_token()
