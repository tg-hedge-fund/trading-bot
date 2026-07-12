import asyncio
import os
import signal
import sys
from threading import Event

import schedule
import uvicorn

from api_utils.groww_api_handlers import refresh_groww_credentials
from api_utils.wrapper_api import app
from strategies.golden_cross import (
    get_crossover_for_all_indices,
)
from strategies.portfolio_summary import get_portfolio_details
from utils.constants import MESSAGE_TYPES
from utils.discord_bot import (
    send_message_via_discord_bot,
    start_discord_bot_instance,
    stop_discord_bot,
)
from utils.jobs import (
    generate_token_every_morning,
    run_job_every_mon_fri,
    run_job_everyday,
    shutdown_job_executor,
)
from utils.utils import config, logger, run_thread

# Global event for graceful shutdown
schedule_shutdown_event = Event()

threads = []
uvicorn_server = None

WRAPPER_API_PORT = config.get("wrapper_api.port")
WRAPPER_API_HOST = config.get("wrapper_api.host")
WRAPPER_API_LOG_LEVEL = "debug"

# wrapper-apis
def run_wrapper_api():
    """Run uvicorn server with graceful shutdown support"""
    global uvicorn_server

    config_obj = uvicorn.Config(
        app,
        host=str(WRAPPER_API_HOST),
        port=int(str(WRAPPER_API_PORT)),
        log_level=WRAPPER_API_LOG_LEVEL
    )
    uvicorn_server = uvicorn.Server(config_obj)

    # Run the server - it will be stopped via shutdown_uvicorn_server()
    asyncio.run(uvicorn_server.serve())


def shutdown_uvicorn_server():
    """Gracefully shutdown the uvicorn server"""
    global uvicorn_server

    if uvicorn_server is not None:
        logger.info("Initiating uvicorn server graceful shutdown...")
        # Set the should_exit flag to trigger graceful shutdown
        uvicorn_server.should_exit = True
        logger.info("Uvicorn server shutdown signal sent")


# schedules
def run_token_generator_schedule():
    try:
        token_scheduler = schedule.Scheduler()
        run_job_everyday(token_scheduler, "07:00", generate_token_every_morning)
        run_job_everyday(token_scheduler, "07:01", refresh_groww_credentials)
        while not schedule_shutdown_event.is_set():
            token_scheduler.run_pending()
            if schedule_shutdown_event.wait(5):
                break
        logger.info("Token scheduler thread shutting down gracefully")
    except Exception as e:
        send_message_via_discord_bot(f"Error in instrument and token schedule thread: {e}", MESSAGE_TYPES.LOGS)
        logger.error(f"Error in instrument and token schedule thread: {e}", exc_info=True)


def run_golden_cross_schedule():
    golden_cross_scheduler = schedule.Scheduler()
    try:
        logger.info("Starting golden cross schedule thread")
        for time in ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00"]:
            run_job_every_mon_fri(golden_cross_scheduler, time, get_crossover_for_all_indices)

        while not schedule_shutdown_event.is_set():
            golden_cross_scheduler.run_pending()
            if schedule_shutdown_event.wait(5):
                break
        logger.info("Golden cross schedule thread shutting down gracefully")
    except Exception as e:
        send_message_via_discord_bot(f"Error in golden cross schedule thread: {e}", MESSAGE_TYPES.LOGS)
        logger.error(f"Error in golden cross schedule thread: {e}", exc_info=True)


def run_portfolio_summary_schedule():
    try:
        pf_scheduler = schedule.Scheduler()
        logger.info("Starting portfolio summary schedule thread")
        run_job_everyday(pf_scheduler, "16:00", get_portfolio_details)

        while not schedule_shutdown_event.is_set():
            pf_scheduler.run_pending()
            if schedule_shutdown_event.wait(60):
                break
        logger.info("Portfolio summary schedule thread shutting down gracefully")
    except Exception as e:
        send_message_via_discord_bot(f"Error in portfolio summary schedule thread: {e}", MESSAGE_TYPES.LOGS)
        logger.error(f"Error in portfolio summary schedule thread: {e}", exc_info=True)


def discord_bot_heartbeat():
    heartbeat_scheduler = schedule.Scheduler()
    def send_heartbeat():
        send_message_via_discord_bot("HEARTBEAT", MESSAGE_TYPES.HEARTBEAT)

    try:
        logger.info("Starting Heartbeat Thread")
        heartbeat_scheduler.every(5).minutes.do(send_heartbeat)

        while not schedule_shutdown_event.is_set():
            heartbeat_scheduler.run_pending()
            if schedule_shutdown_event.wait(60):
                break
        logger.info("Discord bot heartbeat thread shutting down gracefully")
    except Exception as e:
        logger.error(f"Error in Discord bot heartbeat thread: {e}", exc_info=True)


async def run_discord_bot():
    try:
        logger.info("Starting Discord bot")
        await start_discord_bot_instance()
        send_message_via_discord_bot(f"Started application on {os.getenv('TGHF_ENV')}...", MESSAGE_TYPES.LOGS)
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
    """Handle shutdown signals (SIGINT, SIGTERM)"""
    logger.info(f"Received signal {signum}. Starting graceful shutdown...")

    # Signal uvicorn to shutdown
    shutdown_uvicorn_server()

    # Signal all other threads to shutdown
    schedule_shutdown_event.set()
    shutdown_job_executor()
    wait_for_threads()


def wait_for_threads(timeout=30):
    """Wait for all threads to complete with timeout"""
    logger.info("Waiting for all threads to complete...")
    # start_time = asyncio.get_event_loop().time() if asyncio._get_running_loop() is None else 0

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

        # api thread - disabling this
        # threads.append(run_thread(run_wrapper_api,name="run_wrapper_api"))
        # logger.info(f"Wrapper API thread started on {WRAPPER_API_HOST}:{WRAPPER_API_PORT}")

        # Start scheduler threads
        threads.append(run_thread(run_token_generator_schedule, name="run_token_generator_schedule"))
        logger.info("Instrument and token schedule thread started")

        threads.append(run_thread(discord_bot_heartbeat,name="discord_bot_heartbeat"))
        logger.info("Discord bot heartbeat thread started")

        if config.get("golden_cross_schedule"):
            threads.append(run_thread(run_golden_cross_schedule,name="run_golden_cross_schedule"))
            logger.info("Golden cross schedule thread started")

        threads.append(run_thread(run_portfolio_summary_schedule, name="run_portfolio_summary_schedule"))
        logger.info("Portfolio summary schedule thread started")

        if not threads:
            logger.warning("No threads were configured to run")

        # Run the Discord bot on the main event loop
        # This will block until the bot is stopped via signal handler
        asyncio.run(run_discord_bot())

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        shutdown_handler(signal.SIGINT, None)
        # wait_for_threads()
    except Exception as e:
        logger.error(f"Unexpected error in main thread: {e}", exc_info=True)
        shutdown_handler(signal.SIGTERM, None)
        # wait_for_threads()
        sys.exit(1)
    else:
        logger.info("Trading Bot Application shutdown complete")
        sys.exit(0)
