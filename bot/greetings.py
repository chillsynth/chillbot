import os
from discord.ext import commands
from asyncio import sleep
import discord
import logging


class Greetings(commands.Cog):
    def __init__(self, bot):
        # Variables to pre-load
        self.online_role = None
        self.current_guild = None

        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.INFO)

        self.vars_loaded = False
        self.get_vars()
        self.bot = bot

    def get_vars(self):
        if not self.vars_loaded:
            try:
                self.logger.info(f"Greetings.cog: GETTING VARS READY...")

                # Get the online for lookup later
                self.current_guild = self.bot.get_guild(int(os.getenv("DEV!_GUILD_ID")))  # TODO: REPLACE LIVE ENV
                self.online_role = discord.utils.get(self.current_guild.roles, name="Online")

                self.vars_loaded = True
                pass
            except AttributeError:
                self.logger.error(f"Greetings.cog: Attribute Error in loading of variables!")
                return None

    async def cog_load(self):
        self.logger.info(f"Greetings.cog: LOADED!")

    # Member Greeting Embed
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not before.bot:
            if before.pending is True and after.pending is False:
                if self.online_role not in before.roles:  # Once onboarded and verified
                    await sleep(0.2)

                    lounge_channel = discord.utils.get(self.current_guild.channels, name="chill-lounge")

                    # Add "Online" role
                    await after.add_roles(discord.utils.get(self.current_guild.roles, name="Online"))

                    welcome_embed = discord.Embed(
                        description=f"Head over to <#{os.getenv('DEV!_GET_ROLES_ID')}> to grab your roles."
                                    f"\nAnd remember to **`GIVE`** <#{os.getenv('DEV!_FEEDBACK_ID')}> "
                                    f"before you **`ASK`** for it!",
                        colour=13281772
                    )  # TODO: REPLACE LIVE ENV
                    welcome_embed.set_footer(text=f"If you have any questions, feel free to @ one of our moderators!")

                    await lounge_channel.send(f"**Hello {before.mention} and welcome to ChillSynth!**")
                    await lounge_channel.send(embed=welcome_embed)


async def setup(bot):
    await bot.add_cog(Greetings(bot))
