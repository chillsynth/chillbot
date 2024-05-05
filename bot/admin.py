from discord.ext import commands
from discord import app_commands
import discord
import logging


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.INFO)

    async def cog_load(self):
        self.logger.info(f"Admin.cog: LOADED!")

    @commands.is_owner()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.command(name="kill_process", description="Terminates bot process safely - !CAUTION!")
    async def stop_bot(self, interaction: discord.Interaction.response):
        await interaction.response.defer()
        await interaction.followup.send(content=f"Terminating bot process now...")
        await self.bot.close()
        self.logger.critical(f"Admin.cog: !!!SHUTDOWN!!!")
        quit(0)

    # Gets bot latency
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction):
        """Gets bot latency"""
        await interaction.response.defer(thinking=True)
        embed = discord.Embed(title='**Current Latency**',
                              description=f"Retrieved latest bot latency",
                              color=0xeee657)
        embed.add_field(name="Latency", value=f'**{round(self.bot.latency * 1000)}**ms')

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Admin(bot))
