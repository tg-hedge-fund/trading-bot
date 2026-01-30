import os

import discord
from dotenv import load_dotenv

from utils.config_reader import ConfigReader

ENV = os.getenv("HF_ENV", "dev")
config = ConfigReader()

load_dotenv(f".env.{ENV}")
TOKEN = os.getenv("DISCORD_TOKEN")

class DiscordClient(discord.Client):
    user: discord.ClientUser

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print(f'We have logged in as {self.user}')

    async def on_message(self, message):
        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

    async def send_message(self, channel, message):
        await channel.send(message)
