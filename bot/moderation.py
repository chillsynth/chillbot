import discord
import sys
import logging
import os
from discord.ext import commands
from discord import app_commands


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.INFO)

        self.ctx_menu = app_commands.ContextMenu(
            name='Report Message',
            callback=self.report_message,
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    async def cog_load(self):
        self.logger.info(f"Moderation.cog: LOADED!")

    # #demos #feedback moderation and SECRET!!!!!
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:  # Don't reply to itself
            return
        if message.channel.name == "demos":  # In demos channel
            if message.content:  # If message has anything but an attachment
                self.logger.info(f"Moderation.cog: {message.author.id} tried to send text in #demos.")
                await message.delete()
                await message.channel.send(content=f"<@{message.author.id}>, "
                                                   f"this channel is for uploading files **only**.",
                                           delete_after=6.0)
            elif message.stickers:  # User sent a sticker
                self.logger.info(f"Moderation.cog: {message.author.id} tried to send a sticker in #demos.")
                await message.delete()
                await message.channel.send(content=f"<@{message.author.id}>, "
                                                   f"this channel is for uploading files **only**.",
                                           delete_after=6.0)

        if message.channel.name == "feedback":  # In feedback channel
            user_id = message.author.id
            channel = message.channel
            last_message = False

            async for msg in channel.history(limit=1000, before=message):
                if msg.author.id == message.author.id:  # Found last message from user
                    last_message = msg
                    print(last_message.content)
                    break  # TODO FINISH FEEDBACK MODERATION

            print(channel.history)

            if not last_message:  # Last message not found - Limit too small / No message sent yet
                print("No last message found.")

        elif not message.guild:  # Message is in DMs
            if "!secret" in message.content.lower():
                # await message.response.send_modal(Report())
                # chillsynth_id = self.bot.get_guild(int(os.getenv("DEBUG_GUILD_ID")))
                # log_channel = discord.utils.get(chillsynth_id.channels, name="moderator-chat")
                message.channel.send(f"Congrats <@{message.author.id}>, you found the secret.")
                self.logger.info(f"Moderation.cog: {message.author.display_name}[{message.author.id}] found the secret")
                sys.stdout.write(f"DM received from {message.author.display_name}[{message.author.id}]")

    @app_commands.checks.has_role(int(os.getenv('DEV!_MOD_ROLE_ID')))  # Change to LIVE
    @app_commands.command(name="username", description="Change the server username of a member")
    async def username_change(self, interaction: discord.Interaction, member: discord.Member, new_username: str):
        await member.edit(nick=new_username)  # TODO: Report to logs
        await interaction.response.send_message(f"### Changed username of <@{member.id}> to `{new_username}`.")

    # REPORT MESSAGE
    @app_commands.default_permissions(use_application_commands=True)
    @app_commands.checks.has_permissions(use_application_commands=True)
    async def report_message(self, interaction: discord.Interaction, message: discord.Message) -> None:
        await interaction.response.send_message(
            f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
        )
        report_log_channel = discord.utils.get(interaction.guild.channels, name="moderator-chat")
        # Handle report by sending it into a log channel
        # log_channel = discord.utils.get(interaction.guild.channels, name="moderator-chat")
        embed = discord.Embed(title='Reported Message',
                              colour=discord.Colour.red())
        if message.content:
            embed.description = message.content

        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.timestamp = message.created_at

        url_view = discord.ui.View()
        url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

        # await report_log_channel.send(f"{mod_role.mention}")  # Tag Moderators
        await report_log_channel.send(embed=embed, view=url_view)
        self.logger.info(f"Moderation.cog: {interaction.user.display_name}[{interaction.user.id}] sent a report.")

    # Removes image posting permissions from specified user
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.command(name="noimg", description="Toggle noimg role for user")
    async def noimg(self, interaction: discord.Interaction, member: discord.Member):
        noimg_role = discord.utils.get(interaction.guild.roles, name="no img :(")
        va_role = discord.utils.get(interaction.guild.roles, name="Visual Artist")
        en_msg = "Removed image posting permissions"
        dis_msg = "Restored image posting permissions"

        if noimg_role not in member.roles:
            await member.add_roles(noimg_role, reason=en_msg)
            if va_role in member.roles:
                await member.remove_roles(va_role, reason=en_msg)
            fin_msg = en_msg
        else:
            await member.remove_roles(noimg_role, reason=en_msg)
            fin_msg = dis_msg

        await interaction.response.send_message(f"{fin_msg} for user {member.mention}")
        self.logger.info(f"Moderation.cog: {fin_msg} for user {member.display_name}[{member.id}]")

    # Create Invite
    @app_commands.command()
    async def create_invite(self, interaction: discord.Interaction, channel: discord.TextChannel,
                            age: int, uses: int):
        invite = await channel.create_invite(max_age=age, max_uses=uses)
        await interaction.channel.send(f"Successfully created invite: {str(invite)} for channel <#{channel.id}>")
        self.logger.info(f"Moderation.cog: Created an invite: {str(invite)} for channel {channel.name}")

# USER REPORT MODAL

# class Report(discord.ui.Modal, title='Report'):
#     report = discord.ui.TextInput(
#         label="What are you reporting?",
#         style=discord.TextStyle.long,
#         placeholder="Please include as much detail as you can...",
#         required=True,
#         min_length=1,
#         max_length=2000
#     )
#
#     async def on_submit(self, interaction: discord.Interaction):
#         report_embed = discord.Embed(title=f"User Report",
#                                      description=f"**{self.report}**\n\nUser ID:{interaction.user.id}",
#                                      timestamp=datetime.now(),
#                                      colour=discord.Colour.red())
#         user_avatar = interaction.user.display_avatar
#         report_embed.set_author(name=interaction.user, icon_url=user_avatar.url)
#         report_embed.set_thumbnail(url=user_avatar.url)
#
#         chillsynth_id = self.bot.get_guild(int(os.getenv("DEBUG_GUILD_ID")))
#         log_channel = discord.utils.get(chillsynth_id.channels, name="moderator-chat")
#
#         log_channel.send(embed=report_embed)
#         sys.stdout.write(f"DM Report Received from {interaction.user.display_name}")
#
#     async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
#         await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
#
#         print(error)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
