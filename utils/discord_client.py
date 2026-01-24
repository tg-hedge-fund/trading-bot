import discord

from utils.config_reader import ConfigReader

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

config = ConfigReader()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

token = str(config.get("discord.secretToken"))
client.run(str(token))
