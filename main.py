import asyncio
import logging
import signal
import sys
from threading import Event, Thread

import schedule

from strategies.golden_cross import (
    get_live_quote_by_hour,
)
from utils.config_reader import ConfigReader
from utils.discord_bot import send_message_via_discord_bot, start_discord_bot_instance
from utils.jobs import (
    generate_token_every_morning_mtof,
    run_job_every_mon_fri,
    scheduled_jobs_instrument,
)

config = ConfigReader()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global event for graceful shutdown
schedule_shutdown_event = Event()
threads = []

#schedules
def run_instrument_and_token_schedule():
    try:
        logger.info("Starting instrument and token schedule thread")
        schedule.every().sunday.do(scheduled_jobs_instrument, "IDX")
        run_job_every_mon_fri("08:00", scheduled_jobs_instrument, "EQ")
        run_job_every_mon_fri("06:00", generate_token_every_morning_mtof)

        # Run the scheduler loop continuously
        while not schedule_shutdown_event.is_set():
            schedule.run_pending()
            if schedule_shutdown_event.wait(60):
                break
        logger.info("Instrument and token schedule thread shutting down gracefully")
    except Exception as e:
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
            # schedule.every().__getattribute__(day).at("16:15").do(get_live_quote_by_hour)

        while not schedule_shutdown_event.is_set():
            schedule.run_pending()
            if schedule_shutdown_event.wait(60):
                break
        logger.info("Golden cross schedule thread shutting down gracefully")
    except Exception as e:
        logger.error(f"Error in golden cross schedule thread: {e}", exc_info=True)

def run_golden_cross_schedule_2():
    def test_run():
        send_message_via_discord_bot("test run")

    try:
        logger.info("Starting Test Thread")
        schedule.every().minute.do(test_run)

        while not schedule_shutdown_event.is_set():
            schedule.run_pending()
            if schedule_shutdown_event.wait(60):
                break
        logger.info("Golden cross schedule thread shutting down gracefully")
    except Exception as e:
        logger.error(f"Error in golden cross schedule thread: {e}", exc_info=True)


def run_discord_bot():
    """Run the Discord bot in its own event loop"""
    try:
        logger.info("Starting Discord bot")
        asyncio.run(start_discord_bot_instance())
    except Exception as e:
        logger.error(f"Error running Discord bot: {e}", exc_info=True)


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
        # Start Discord bot in its own thread with its own event loop
        discord_bot_thread = Thread(target=run_discord_bot, name="discord_bot")
        discord_bot_thread.daemon = False
        threads.append(discord_bot_thread)
        discord_bot_thread.start()
        logger.info("Discord bot thread started")

        if config.get("instrument_and_token_schedule"):
            instrument_and_token_schedule = Thread(target=run_instrument_and_token_schedule, name="instrument_and_token_schedule")
            instrument_and_token_schedule.daemon = False
            threads.append(instrument_and_token_schedule)
            instrument_and_token_schedule.start()
            logger.info("Instrument and token schedule thread started")

        if config.get("golden_cross_schedule"):
            golden_cross_schedule = Thread(target=run_golden_cross_schedule, name="golden_cross_schedule")
            golden_cross_schedule.daemon = False
            threads.append(golden_cross_schedule)
            golden_cross_schedule.start()
            logger.info("Golden cross schedule thread started")

        if config.get("golden_cross_schedule"):
            golden_cross_schedule_2 = Thread(target=run_golden_cross_schedule_2, name="golden_cross_schedule_2")
            golden_cross_schedule_2.daemon = False
            threads.append(golden_cross_schedule_2)
            golden_cross_schedule_2.start()
            logger.info("test schedule thread started")

        if not threads:
            logger.warning("No scheduler threads were configured to run")

        # Keep the main thread alive
        while threads and any(t.is_alive() for t in threads):
            for thread in threads:
                thread.join(timeout=1)

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
