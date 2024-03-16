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

        self.bot = bot

    async def cog_load(self):
        self.logger.info(f"Greetings.cog: LOADED!")

    # Member Greeting Embed
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not before.bot:
            if before.pending is True and after.pending is False:
                if self.online_role not in before.roles:  # Once onboarded and verified
                    await sleep(0.2)

                    the_guild: discord.Guild = await self.bot.fetch_guild(int(os.getenv("DEV_GUILD_ID")))
                    lounge_channel: discord.TextChannel = await the_guild.fetch_channel(
                        int(os.getenv("DEV_LOUNGE_ID")))

                    # Add "Online" role
                    await after.add_roles(the_guild.get_role(int(os.getenv("DEV_ONLINE_ROLE_ID"))))

                    welcome_embed = discord.Embed(
                        description=f"### <:Discord_Invite:1140057489941995650>"
                                    f"   Head over to <#{os.getenv('DEV_GET_ROLES_ID')}> to grab your roles"
                                    f"\n### <:Discord_Message_SpeakTTS:1140059207106826271>"
                                    f"   And remember to **`GIVE`** <#{os.getenv('DEV_FEEDBACK_ID')}> "
                                    f"__before__ you **`ASK`** for it!",
                        colour=13281772
                    )
                    welcome_embed.set_footer(text=f"If you have any questions, feel free to @ one of our moderators!")

                    await lounge_channel.send(f"**Hello {before.mention} and welcome to ChillSynth!**")
                    await lounge_channel.send(embed=welcome_embed)


async def setup(bot):
    await bot.add_cog(Greetings(bot))
