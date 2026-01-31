import asyncio
import logging
import os
from threading import Event, Thread
from time import time

import discord
from dotenv import load_dotenv

from utils.config_reader import ConfigReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ENV = os.getenv("HF_ENV", "dev")
config = ConfigReader()

load_dotenv(f".env.{ENV}")
TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

class DiscordBot(discord.Client):
    user: discord.ClientUser
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ready_event = Event()  # Use threading.Event for cross-loop synchronization
        self.bot = Thread(target=self.run, args=(str(TOKEN),), daemon=True)
        logger.info("DiscordBot initialized")

class DiscordClient(DiscordBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.bot.is_alive():
            logger.info("Bot thread already alive")
        else:
            self.bot.start()
            logger.info("Discord bot thread started")

    async def on_ready(self):
        logger.info(f'We have logged in as {self.user}')
        self.ready_event.set()

    async def on_message(self, message):
        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

    async def wait_until_ready(self, timeout=30):
        logger.info("Waiting for bot to be ready...")
        loop = asyncio.get_event_loop()
        # Use run_in_executor to wait for the threading.Event in a non-blocking way
        await loop.run_in_executor(None, self.ready_event.wait, timeout)
        logger.info("Bot is ready!")

    async def send_message(self, message):
        logger.info(f"send_message called with: {message}")

        if self.is_ready():
            try:
                CHANNEL_ID = int(str(DISCORD_CHANNEL_ID))
                channel = self.get_channel(CHANNEL_ID)
                if channel:
                    assert isinstance(channel, discord.abc.Messageable)
                    future = asyncio.run_coroutine_threadsafe(
                        channel.send(str(message)),
                        self.loop
                    )
                    result = await asyncio.get_event_loop().run_in_executor(None, future.result)
                    logger.info(f"Message sent successfully: {result}")
                else:
                    logger.error(f"Channel not found with ID: {CHANNEL_ID}")
                    logger.info(f"Available channels: {[(c.name, c.id) for c in self.get_all_channels()]}")
            except Exception as e:
                logger.error(f"Error sending message: {e}", exc_info=True)
        else:
            logger.error("Client isn't ready")
