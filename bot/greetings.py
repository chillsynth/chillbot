import os
from discord.ext import commands
from asyncio import sleep
import discord


class Greetings(commands.Cog):
    def __init__(self, bot):
        # Variables to pre-load
        self.online_role = None
        self.feedback_channel = None
        self.get_roles_channel = None

        self.vars_loaded = False
        self.get_vars()
        self.bot = bot

    def get_vars(self):
        print(self.vars_loaded)
        if not self.vars_loaded:
            try:
                self.online_role = self.bot.get_guild(int(os.getenv("DEBUG_GUILD_ID")))
                print(self.get_roles_channel)
                print(self.feedback_channel)
                print(f"`Greetings` variables loaded")
                self.vars_loaded = True
            except AttributeError:
                print("Attribute Error in loading of variables")
                return None

    async def cog_load(self):
        self.get_vars()
        print(f"`Greetings` cog loaded")

    # Member Greeting Embed
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not before.bot:
            if before.pending is True and after.pending is False:
                if self.online_role not in before.roles:  # Once onboarded and verified
                    await sleep(0.2)
                    test_guild = self.bot.get_guild(int(os.getenv("DEBUG_GUILD_ID")))  # YAY! guild object :catJAM:
                    lounge_channel = discord.utils.get(test_guild.channels, name="chill-lounge")

                    await after.add_roles(discord.utils.get(test_guild.roles, name="Online"))  # Add "Online" role

                    welcome_embed = discord.Embed(
                        description=f"Head over to <#{os.getenv('GET_ROLES_ID')}> to grab your roles."
                                    f"\nAnd remember to **`GIVE`** <#{os.getenv('FEEDBACK_ID')}> "
                                    f"before you **`ASK`** for it!",
                        colour=13281772
                    )
                    welcome_embed.set_footer(text=f"If you have any questions, feel free to @ one of our moderators!")

                    await lounge_channel.send(f"**Hello {before.mention} and welcome to ChillSynth!**")
                    await lounge_channel.send(embed=welcome_embed)


async def setup(bot):
    await bot.add_cog(Greetings(bot))
