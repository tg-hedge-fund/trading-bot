import asyncio
import logging
import os
from threading import Thread
from time import time

import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.config_reader import ConfigReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ENV = os.getenv("HF_ENV", "dev")
config = ConfigReader()

load_dotenv(f".env.{ENV}")
TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

# class DiscordBot(discord.Client):
#     user: discord.ClientUser
#     _bot = None

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         if self._bot is None:
#             try:
#                 # use when bot is needed to reply to your commands
#                 # self._bot = commands.Bot(command_prefix=command_prefix, description=description, intents=)
#                 # self._bot = Thread(target=self._run_bot, daemon=True)
#                 logger.info("Discord Bot is now online")
#             except RuntimeError:
#                 print("Failed in init of asynio event loop")

class DiscordClient(discord.Client):
    # _instance = None
    # _initialized = False

    # def __new__(cls):
    #     if cls._instance is None:
    #       cls._instance = super().__new__(cls)
    #     return cls._instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ready_event = asyncio.Event()

    async def on_ready(self):
        logger.info(f'We have logged in as {self.user}')
        self._ready_event.set()

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

    async def send_message(self, message):
        logger.info(f"send_message called with: {message}")

        if self.is_ready():
            try:
                CHANNEL_ID = int(str(DISCORD_CHANNEL_ID))
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
        raise

    return _bot_instance

async def send_message_via_discord_bot(message):
    """Send a message via the Discord bot"""
    _bot_instance = await start_discord_bot_instance()
    await _bot_instance.send_message(message)

async def stop_discord_bot():
    """Gracefully stop the Discord bot"""
    global _bot_instance, _bot_task

    if _bot_instance is not None and not _bot_instance.is_closed():
        try:
            logger.info("Stopping Discord bot...")
            await _bot_instance.close()
            _bot_instance = None
            if _bot_task is not None:
                try:
                    await asyncio.wait_for(_bot_task, timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning("Bot stop task timed out")
                _bot_task = None
            logger.info("Discord bot stopped")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}", exc_info=True)


