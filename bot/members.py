import os

from discord.ext import commands
from discord import app_commands
import discord
from datetime import *
import logging


class Members(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.INFO)

    async def cog_load(self):
        self.logger.info(f"Members.cog: LOADED!")

    # MEMBER JOIN PROCESS
    @commands.Cog.listener()
    async def on_member_join(self, new_member: discord.Member):
        if new_member.system:  # Official Discord User
            self.logger.info(f"WOAH! {new_member.global_name} is a system user :)")
            print(f"WOAH! {new_member.global_name} is a system user :)")

    @app_commands.command(name="feedback", description="Submit user feedback")
    async def feedback(self, interaction: discord.Interaction.response):
        """Send feedback to the server team"""
        await interaction.response.send_modal(Feedback())

    @app_commands.command(name="report", description="Submit a report")
    async def report(self, interaction: discord.Interaction.response):
        """Send report to the mod team"""
        await interaction.response.send_modal(UserReport())


# USER REPORT MODAL
class UserReport(discord.ui.Modal, title='Report'):
    reportedUserID = discord.ui.TextInput(
        label="What would you like to report?",
        style=discord.TextStyle.short,
        placeholder="Include 'Username#0000' or user ID",
        required=True,
        min_length=6,
        max_length=36
    )

    report = discord.ui.TextInput(
        label="What would you like to report?",
        style=discord.TextStyle.long,
        placeholder="Please write as much detail as possible...",
        required=True,
        min_length=1,
        max_length=2000
    )

    async def on_submit(self, interaction: discord.Interaction.response):
        embed = discord.Embed(title=f"Reported Username / ID: {self.reportedUserID}",
                              description=f"**{self.report}**\n",
                              timestamp=datetime.now(),
                              colour=discord.Colour.red())
        user_avatar = interaction.user.display_avatar
        embed.set_author(name=f"Submitted by: {interaction.user}", icon_url=user_avatar.url)
        embed.set_thumbnail(url="https://i.imgur.com/giZ2D5T.gif")

        channel: discord.TextChannel = discord.utils.get(interaction.guild.channels, name="moderator-chat")
        await channel.send(f"### {interaction.guild.get_role(int(os.getenv('DEV_MOD_ROLE_ID'))).mention}"
                           f"\n# <:Discord_System_MessageInteractio:1140060017853210696>  **NEW REPORT**")
        await channel.send(embed=embed)

        await interaction.response.send_message(f'Thanks for your report, {interaction.user.display_name}!',
                                                ephemeral=True)

    async def on_error(self, interaction: discord.Interaction.response, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        logger = logging.getLogger('discord')
        logger.setLevel(logging.INFO)
        logger.error(f"{error}")


# USER FEEDBACK MODAL
class Feedback(discord.ui.Modal, title='Feedback'):
    feedback = discord.ui.TextInput(
        label="What would you like to feedback?",
        style=discord.TextStyle.long,
        placeholder="Type your feedback here...",
        required=True,
        min_length=0,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction.response):
        embed = discord.Embed(title=f"User Feedback",
                              description=f"**{self.feedback}**\n\nUser ID:{interaction.user.id}",
                              timestamp=datetime.now(),
                              colour=discord.Colour.yellow())
        user_avatar = interaction.user.display_avatar
        embed.set_author(name=interaction.user, icon_url=user_avatar.url)
        embed.set_thumbnail(url=user_avatar.url)

        channel: discord.TextChannel = discord.utils.get(interaction.guild.channels, name="user-feedback")
        await channel.send(embed=embed)

        await interaction.response.send_message(f'Thanks for your feedback, {interaction.user.name}!', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction.response, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        logger = logging.getLogger('discord')
        logger.setLevel(logging.INFO)
        logger.error(f"{error}")


async def setup(bot):
    await bot.add_cog(Members(bot))
