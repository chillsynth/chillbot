from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import traceback
from datetime import datetime
import discord
import os

load_dotenv()


class CogTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction):
        """Gets bot latency"""
        embed = discord.Embed(title='**Current Latency**',
                              description=f"Retrieved latest bot latency",
                              color=0xeee657)
        embed.add_field(name=None, value=f'Latency: **{round(self.bot.latency * 1000)}**ms')
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="feedback", description="Submit feedback")
    async def feedback(self, interaction: discord.Interaction):
        """Send feedback to the server team"""
        await interaction.response.send_modal(Feedback())


class Feedback(discord.ui.Modal, title='Feedback'):
    feedback = discord.ui.TextInput(
        label="What would you like to feedback?",
        style=discord.TextStyle.long,
        placeholder="Type your feedback here...",
        required=True,
        min_length=0,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"User Feedback",
                              description=f"**{self.feedback}**\n\nUser ID:{interaction.user.id}",
                              timestamp=datetime.now(),
                              colour=discord.Colour.yellow())
        user_avatar = interaction.user.display_avatar
        embed.set_author(name=interaction.user, icon_url=user_avatar.url)
        embed.set_thumbnail(url=user_avatar.url)

        channel = discord.utils.get(interaction.guild.channels, name="moderator-chat")
        await channel.send(embed=embed)

        await interaction.response.send_message(f'Thanks for your feedback, {interaction.user.name}!', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        print(error)


async def setup(bot):
    await bot.add_cog(CogTest(bot))
