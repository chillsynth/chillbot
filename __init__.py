# import logging
# import logging.handlers
import asyncio
import os
from dotenv import load_dotenv
from typing import List, Optional
import discord
from discord.ext import commands
from aiohttp import ClientSession

load_dotenv()


class ChillBot(commands.Bot):
    def __init__(
            self,
            *args,
            initial_extensions: List[str],
            web_client: ClientSession,
            testing_guild_id: Optional[int] = os.getenv("DEBUG_GUILD_ID"),
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.web_client = web_client
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_extensions

    async def on_ready(self):
        print(f"<{self.user.name} [{self.user.id}] is ready and online!>")

    async def setup_hook(self) -> None:
        # here, we are loading extensions prior to sync to ensure we are syncing
        # interactions defined in those extensions.

        for extension in self.initial_extensions:
            await self.load_extension(extension)

        # In overriding setup hook,
        # we can do things that require a bot prior to starting to process events from the websocket.
        # In this case, we are using this to ensure that once we are connected, we sync for the testing guild.
        # You should not do this for every guild or for global sync, those should only be synced when changes happen.
        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            # We'll copy in the global commands to test with:
            self.tree.copy_global_to(guild=guild)
            # followed by syncing to the testing guild.
            await self.tree.sync(guild=guild)

        # This would also be a good place to connect to our database and
        # load anything that should be in memory prior to handling events.


async def main():
    # When taking over how the bot process is run, you become responsible for a few additional things.

    # 1. logging
    # for this example, we're going to set up a rotating file logger.
    # for more info on setting up logging,
    # see https://discordpy.readthedocs.io/en/latest/logging.html and https://docs.python.org/3/howto/logging.html
    #
    # logger = logging.getLogger('discord')
    # logger.setLevel(logging.INFO)
    #
    # handler = logging.handlers.RotatingFileHandler(
    #     filename='discord.log',
    #     encoding='utf-8',
    #     maxBytes=32 * 1024 * 1024,  # 32 MiB
    #     backupCount=5,  # Rotate through 5 files
    # )
    # dt_fmt = '%Y-%m-%d %H:%M:%S'
    # formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)

    # Alternatively, you could use:
    # discord.utils.setup_logging(handler=handler, root=False)

    # One of the reasons to take over more of the process though
    # is to ensure use with other libraries or tools which also require their own cleanup.

    # Here we have a web client and a database pool, both of which do cleanup at exit.
    # We also have our bot, which depends on both of these.

    async with ClientSession() as our_client:
        # 2. We become responsible for starting the bot.
        print(f"\n<Starting>")
        extensions = ["members"]
        async with ChillBot(commands.when_mentioned,
                            web_client=our_client,
                            initial_extensions=extensions,
                            intents=discord.Intents.all(),
                            activity=discord.Activity(type=discord.ActivityType.listening,
                                                      name="ChillSynth FM",
                                                      url="https://nightride.fm/eq?station=chillsynth"),
                            status=discord.Status.online) as bot:
            await bot.start(os.getenv('TOKEN'))


# For most use cases, after defining what needs to run, we can just tell asyncio to run it:
asyncio.run(main())
