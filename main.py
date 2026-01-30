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
from utils.discord_bot import TOKEN, DiscordClient
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

def run_discord_bot_async():
    intents = discord.Intents.default()
    intents.message_content = True

    discord_client = DiscordClient(intents=intents)

    # Run bot in background thread
    bot_thread = Thread(target=discord_client.run, args=(str(TOKEN),), daemon=True)
    bot_thread.start()

    # Wait for the client to be ready
    timeout = 30
    for i in range(timeout * 10):
        if discord_client.is_ready():
            break
        time.sleep(0.1)

    if discord_client.is_ready():
        # Get the channel and send message
        channel = discord_client.get_channel(1466891875691659427)
        if channel:
            # Use asyncio to run the async send_message on the bot's event loop
            asyncio.run_coroutine_threadsafe(
                discord_client.send_message(channel, "Hello"),
                discord_client.loop
            )
            print("Message sent")
        else:
            print("Channel not found")
    else:
        print("Bot failed to connect")

if __name__ == "__main__":
    # schedule.every().monday.at("09:16").do(scheduled_jobs_instrument, "EQ")
    # schedule.every().tuesday.at("09:16").do(scheduled_jobs_instrument, "EQ")
    # schedule.every().wednesday.at("09:16").do(scheduled_jobs_instrument, "EQ")
    # schedule.every().thursday.at("09:16").do(scheduled_jobs_instrument, "EQ")
    # schedule.every().friday.at("09:16").do(scheduled_jobs_instrument, "EQ")
    # schedule.every().sunday.do(scheduled_jobs_instrument, "IDX")

    run_discord_bot_async()
