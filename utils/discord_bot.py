import asyncio
import os

import discord
from dotenv import load_dotenv

from utils.utils import logger

ENV = os.getenv("TGHF_ENV", "dev")

load_dotenv(f".env.{ENV}")
TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
HEARTBEAT_DISCORD_CHANNEL_ID = os.getenv("DISCORD_HEARTBEAT_CHANNEL_ID")

class DiscordClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ready_event = asyncio.Event()
        self._message_queue = asyncio.Queue()
        self._worker_task = None

    async def on_ready(self):
        logger.info(f'We have logged in as {self.user}')
        self._ready_event.set()
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._message_worker())

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

    async def _message_worker(self):
        logger.info("Message worker started")
        while True:
            try:
                message = await self._message_queue.get()

                if message is None:
                    logger.info("Message worker shutting down")
                    break

                await self._send_message_via_discord(message)
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Error in message worker: {e}", exc_info=True)

    async def _send_message_via_discord(self, message):
        logger.info(f"send_message called with: {message}")

        if self.is_ready():
            try:
                CHANNEL_ID = int(str(DISCORD_CHANNEL_ID))
                if message == 'HEARTBEAT':
                    CHANNEL_ID = int(str(HEARTBEAT_DISCORD_CHANNEL_ID))
                channel = self.get_channel(CHANNEL_ID)
                if channel:
                    assert isinstance(channel, discord.abc.Messageable)
                    await channel.send(str(message))
                else:
                    logger.error(f"Channel not found with ID: {CHANNEL_ID}")
                    logger.info(f"Available channels: {[(c.name, c.id) for c in self.get_all_channels()]}")
            except Exception as e:
                logger.error(f"Error sending message: {e}", exc_info=True)
        else:
            logger.error("Client isn't ready")

    def queue_message(self, message):
        self._message_queue.put_nowait(message)

    async def wait_for_queue_empty(self):
        try:
            await self._message_queue.join()
        except Exception as e:
            logger.error(f"Error waiting for queue: {e}", exc_info=True)

    async def shutdown_worker(self):
        if self._worker_task:
            try:
                await self._message_queue.put(None)  # Send shutdown signal
                await asyncio.wait_for(self._worker_task, timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("Worker task did not stop in time, cancelling")
                self._worker_task.cancel()
            except Exception as e:
                logger.error(f"Error shutting down worker: {e}", exc_info=True)


_bot_instance = None
_bot_task = None

async def start_discord_bot_instance():
    global _bot_instance, _bot_task

    # Check if bot is already running and connected
    if _bot_instance is not None and not _bot_instance.is_closed():
        logger.info("Discord Bot is already running!")
        return _bot_instance

    intents = discord.Intents.default()
    intents.message_content = True

    _bot_instance = DiscordClient(intents=intents)

    # Start the bot in the background
    _bot_task = asyncio.create_task(_bot_instance.start(str(TOKEN), reconnect=True))

    # Wait for the bot to be ready with a timeout
    try:
        await asyncio.wait_for(_bot_instance._ready_event.wait(), timeout=10.0)
        logger.info("Discord bot is ready!")
    except asyncio.TimeoutError:
        logger.error("Discord bot failed to become ready within 10 seconds")
        try:
            await _bot_instance.close()
        except Exception as e:
            logger.error(f"Error closing bot: {e}")
        _bot_instance = None
        _bot_task = None
        raise RuntimeError("Discord bot initialization timeout")
    except Exception as e:
        logger.error(f"Error waiting for bot to be ready: {e}", exc_info=True)
        try:
            await _bot_instance.close()
        except Exception as close_error:
            logger.error(f"Error closing bot: {close_error}")
        _bot_instance = None
        _bot_task = None
        raise Exception("Discord Bot closed")

    return _bot_instance

def send_message_via_discord_bot(message):
    global _bot_instance
    if _bot_instance is None:
        logger.error("Bot isn't running")
    else:
        _bot_instance.queue_message(message)


async def send_message_via_discord_bot_async(message):
    """Send a message via the Discord bot (async)"""
    global _bot_instance
    if _bot_instance is None:
        logger.error("Bot isn't running")
        try:
            _bot_instance = await start_discord_bot_instance()
        except Exception as e:
            logger.error(f"Failed to start bot: {e}", exc_info=True)
            return

    _bot_instance.queue_message(message)


async def wait_for_empty_discord_message_queue():
    global _bot_instance
    if _bot_instance:
        try:
            await _bot_instance.wait_for_queue_empty()
            await _bot_instance.shutdown_worker()
        except Exception as e:
            logger.error(f"Error waiting for queue: {e}", exc_info=True)


async def stop_discord_bot():
    global _bot_instance, _bot_task

    if _bot_instance is not None and not _bot_instance.is_closed():
        try:
            logger.info("Stopping Discord bot...")

            # First, shutdown the worker to process remaining messages
            await _bot_instance.shutdown_worker()

            # Then close the bot connection
            await _bot_instance.close()
            _bot_instance = None

            # Wait for the bot task to complete
            if _bot_task is not None:
                try:
                    await asyncio.wait_for(_bot_task, timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning("Bot stop task timed out")
                except asyncio.CancelledError:
                    logger.info("Bot task was cancelled")
                except Exception as e:
                    logger.error(f"Error waiting for bot task: {e}", exc_info=True)
                finally:
                    _bot_task = None

            logger.info("Discord bot stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}", exc_info=True)
            _bot_instance = None
            _bot_task = None
