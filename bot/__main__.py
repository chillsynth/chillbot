import logging
import logging.handlers
import asyncio
import os
import motor.motor_asyncio
from typing import List, Optional
import discord
from discord.ext import commands
from aiohttp import ClientSession


class ChillBot(commands.Bot):
    def __init__(
            self,
            *args,
            initial_extensions: List[str],
            web_client: ClientSession,
            testing_guild_id: Optional[int] = os.getenv("DEV_GUILD_ID"),
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.web_client = web_client
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_extensions

    async def on_ready(self):
        print(f"<{self.user.name} [{self.user.id}] is ready and online!>")
        logger = logging.getLogger('discord')
        logger.info(f"<{self.user.name} [{self.user.id}] is ready and online!>")

    async def setup_hook(self) -> None:
        for extension in self.initial_extensions:
            await self.load_extension(extension)

        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            # Copy global commands
            self.tree.copy_global_to(guild=guild)
            # Sync commands to tree
            await self.tree.sync(guild=guild)


async def main():
    # Logging
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)  # TODO: SET TO INFO ON RELEASE

    if not os.path.exists("logs"):
        os.makedirs("logs")

    handler = logging.handlers.RotatingFileHandler(
        filename='logs/discord.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = '%d-%m-%Y %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<5}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    async def return_logger():
        return logger
    # DB Setup
    client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("DEV_MONGO_URI"))
    db = client.test

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        logger.info(f"Connected to MongoDB!")
        # Show connection to DB
        logger.debug(db)
    except Exception as e:
        logger.error(e)

    async with ClientSession() as our_client:
        logger.info(f"<Starting>")  # Startup has begun
        extensions = ["members", "extras", "greetings", "events", "moderation", "admin"]  # "art" v4?
        async with ChillBot(commands.when_mentioned,
                            web_client=our_client,
                            initial_extensions=extensions,
                            intents=discord.Intents.all(),
                            activity=discord.Activity(type=discord.ActivityType.listening,
                                                      name="ChillSynth FM",
                                                      url="https://nightride.fm/eq?station=chillsynth"),
                            status=discord.Status.online) as bot:
            await bot.start(os.getenv('DEV_TOKEN'))


asyncio.run(main())
