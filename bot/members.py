import os

from discord.ext import commands
from discord import app_commands
from datetime import datetime
import discord


class Members(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        print(f"`Members` cog loaded")

    @app_commands.command(name="feedback", description="Submit feedback")
    async def feedback(self, interaction: discord.Interaction):
        """Send feedback to the server team"""
        await interaction.response.send_modal(Feedback())

    @app_commands.command(name="report", description="Submit a report")
    async def report(self, interaction: discord.Interaction):
        """Send report to the mod team"""
        await interaction.response.send_modal(UserReport())


class UserReport(discord.ui.Modal, title='Report'):
    reportedUserID = discord.ui.TextInput(
        label="User’s ID or Username (use if reporting user)",
        style=discord.TextStyle.short,
        placeholder="Include 'Username#0000' or user ID",
        required=False,
        min_length=4,
        max_length=38
    )

    report = discord.ui.TextInput(
        label="What would you like to report?",
        style=discord.TextStyle.long,
        placeholder="Please write as much detail as possible...",
        required=True,
        min_length=1,
        max_length=2000
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"Username / ID: {self.reportedUserID}",
                              description=f"**{self.report}**\n",
                              timestamp=datetime.now(),
                              colour=discord.Colour.red())
        user_avatar = interaction.user.display_avatar
        embed.set_author(name=f"Submitted by: {interaction.user}", icon_url=user_avatar.url)
        embed.set_thumbnail(url="https://i.imgur.com/giZ2D5T.gif")

        channel = discord.utils.get(interaction.guild.channels, name="moderator-chat")
        mod_role = interaction.guild.get_role(int(os.getenv('DEV_MOD_ROLE_ID')))
        await channel.send(f"{mod_role.mention}")
        await channel.send(embed=embed)

        await interaction.response.send_message(f'Thanks for your report, {interaction.user.name}!', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        print(error)


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

        channel = discord.utils.get(interaction.guild.channels, name="user-feedback")
        await channel.send(embed=embed)

        await interaction.response.send_message(f'Thanks for your feedback, {interaction.user.name}!', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        print(error)


async def setup(bot):
    await bot.add_cog(Members(bot))
