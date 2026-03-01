import asyncio
import os
import signal
import sys
from threading import Event, Thread

import schedule

from api.groww_api_handlers import refresh_groww_credentials
from strategies.golden_cross import (
    get_live_quote_by_hour,
)
from utils.discord_bot import (
    send_message_via_discord_bot,
    start_discord_bot_instance,
    stop_discord_bot,
)
from utils.jobs import (
    generate_token_every_morning_mtof,
    run_job_every_mon_fri,
    scheduled_jobs_instrument,
)
from utils.utils import config, logger

# Global event for graceful shutdown
schedule_shutdown_event = Event()
threads = []

# schedules
def run_instrument_and_token_schedule():
    try:
        if config.get("instrument_and_eq_schedule"):
            schedule.every().sunday.do(scheduled_jobs_instrument, "IDX")
            run_job_every_mon_fri("09:15", scheduled_jobs_instrument, "EQ")
        run_job_every_mon_fri("07:00", generate_token_every_morning_mtof)
        run_job_every_mon_fri("07:01", refresh_groww_credentials)

        # Run the scheduler loop continuously
        while not schedule_shutdown_event.is_set():
            schedule.run_pending()
            if schedule_shutdown_event.wait(60):
                break
        logger.info("Instrument and token schedule thread shutting down gracefully")
    except Exception as e:
        send_message_via_discord_bot(f"Error in instrument and token schedule thread: {e}")
        logger.error(f"Error in instrument and token schedule thread: {e}", exc_info=True)


def run_golden_cross_schedule():
    try:
        logger.info("Starting golden cross schedule thread")
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
            schedule.every().__getattribute__(day).at("09:15").do(get_live_quote_by_hour)
            schedule.every().__getattribute__(day).at("10:15").do(get_live_quote_by_hour)
            schedule.every().__getattribute__(day).at("11:15").do(get_live_quote_by_hour)
            schedule.every().__getattribute__(day).at("12:15").do(get_live_quote_by_hour)
            schedule.every().__getattribute__(day).at("13:15").do(get_live_quote_by_hour)
            schedule.every().__getattribute__(day).at("14:15").do(get_live_quote_by_hour)
            schedule.every().__getattribute__(day).at("15:15").do(get_live_quote_by_hour)

        while not schedule_shutdown_event.is_set():
            schedule.run_pending()
            if schedule_shutdown_event.wait(5):
                break
        logger.info("Golden cross schedule thread shutting down gracefully")
    except Exception as e:
        send_message_via_discord_bot(f"Error in golden cross schedule thread: {e}")
        logger.error(f"Error in golden cross schedule thread: {e}", exc_info=True)


def discord_bot_heartbeat():
    def send_heartbeat():
        send_message_via_discord_bot("HEARTBEAT")

    try:
        logger.info("Starting Heartbeat Thread")
        schedule.every(5).minutes.do(send_heartbeat)

        while not schedule_shutdown_event.is_set():
            schedule.run_pending()
            if schedule_shutdown_event.wait(60):
                break
        logger.info("Discord bot shutting down gracefully")
    except Exception as e:
        logger.error(f"Error in Discord bot shutting down gracefully: {e}", exc_info=True)


async def run_discord_bot():
    try:
        logger.info("Starting Discord bot")
        await start_discord_bot_instance()
        send_message_via_discord_bot(f"Started application on {os.getenv("TGHF_ENV")}...")
        # Keep the bot running until shutdown signal
        while not schedule_shutdown_event.is_set():
            await asyncio.sleep(1)
        logger.info("Discord bot shutdown signal received")
    except Exception as e:
        logger.error(f"Error running Discord bot: {e}", exc_info=True)
    finally:
        logger.info("Closing Discord bot connection")
        await stop_discord_bot()


def shutdown_handler(signum, frame):
    logger.info(f"Received signal {signum}. Starting graceful shutdown...")
    schedule_shutdown_event.set()


def wait_for_threads(timeout=30):
    logger.info("Waiting for all threads to complete...")
    for thread in threads:
        thread.join(timeout=timeout)
        if thread.is_alive():
            logger.warning(f"Thread '{thread.name}' did not finish within timeout")
    logger.info("All threads have been terminated")


if __name__ == "__main__":

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    logger.info("Starting Trading Bot Application")

    try:
        # need to add token checker per minute, for expired or fabricated token. fetch user details to check token authenticitly

        # Start scheduler threads first (before Discord bot)
        instrument_and_token_schedule = Thread(
            target=run_instrument_and_token_schedule,
            name="instrument_and_token_schedule",
            daemon=False
        )
        threads.append(instrument_and_token_schedule)
        instrument_and_token_schedule.start()
        logger.info("Instrument and token schedule thread started")

        discord_bot_heartbeat_thread = Thread(
            target=discord_bot_heartbeat,
            name="discord_bot_heartbeat_thread",
            daemon=False
        )
        threads.append(discord_bot_heartbeat_thread)
        discord_bot_heartbeat_thread.start()
        logger.info("discord bot heartbeat thread started")

        if config.get("golden_cross_schedule"):
            golden_cross_schedule = Thread(
                target=run_golden_cross_schedule,
                name="golden_cross_schedule",
                daemon=False
            )
            threads.append(golden_cross_schedule)
            golden_cross_schedule.start()
            logger.info("Golden cross schedule thread started")

        if not threads:
            logger.warning("No scheduler threads were configured to run")

        # Run the Discord bot on the main event loop
        # This will block until the bot is stopped via signal handler
        asyncio.run(run_discord_bot())
        # run_discord_bot()

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        schedule_shutdown_event.set()
        wait_for_threads()
    except Exception as e:
        logger.error(f"Unexpected error in main thread: {e}", exc_info=True)
        schedule_shutdown_event.set()
        wait_for_threads()
        sys.exit(1)
    else:
        logger.info("Trading Bot Application shutdown complete")
        sys.exit(0)
