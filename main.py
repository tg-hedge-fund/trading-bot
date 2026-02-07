import asyncio
import logging
import time
from threading import Thread

import discord
import pandas as pd
import schedule
from discord.ext import commands

from api.historical_data import get_historical_data
from api.portfolio import get_portfolio
from trade_utils.save_instruments import save_instrument_eq, save_instrument_idx
from trade_utils.ta_indicators import calculate_ema, calculate_sma
from utils.app_config import extract_groww_keys
from utils.discord_bot import TOKEN, DiscordClient, send_message_via_discord_bot
from utils.token_generator import generate_token, get_access_token

# ACCESS_TOKEN, GROWW, FEED = get_access_token()

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

async def run_discord_bot():
    for i in range(10):
        await send_message_via_discord_bot(f"message number: {i}")
        await asyncio.sleep(1)
        



if __name__ == "__main__":
    # schedule.every().monday.at("09:16").do(scheduled_jobs_instrument, "EQ")
    # schedule.every().tuesday.at("09:16").do(scheduled_jobs_instrument, "EQ")
    # schedule.every().wednesday.at("09:16").do(scheduled_jobs_instrument, "EQ")
    # schedule.every().thursday.at("09:16").do(scheduled_jobs_instrument, "EQ")
    # schedule.every().friday.at("09:16").do(scheduled_jobs_instrument, "EQ")
    # schedule.every().sunday.do(scheduled_jobs_instrument, "IDX")

    asyncio.run(run_discord_bot())
