from discord.ext import commands
from discord import app_commands
import os
import discord


# import random


class Events(commands.Cog):
    def __init__(self, bot):
        self.vars_loaded = False
        self.get_vars()
        self.bot = bot

    def get_vars(self):
        if not self.vars_loaded:
            try:
                print(f"`Events` variables loaded")
                self.vars_loaded = True
            except AttributeError:
                return None

    async def cog_load(self):
        print(f"`Events` cog loaded")
        self.get_vars()

    # EVENT HOST ONLY
    @app_commands.command(name="event", description="Sets Event Mode on and off.")
    @app_commands.checks.has_role("Event Host")
    @app_commands.choices(
        event_type=[
            discord.app_commands.Choice(name="Stage", value=0),
            discord.app_commands.Choice(name="Stream", value=1)
        ]
    )
    async def event(self, interaction: discord.Interaction,
                    event_type: discord.app_commands.Choice[int],
                    enable: bool):
        test_guild = self.bot.get_guild(int(os.getenv("DEBUG_GUILD_ID")))  # YAY! guild object :catJAM:
        event_stage = discord.utils.get(test_guild.channels, name="Event Stage")
        event_stream = discord.utils.get(test_guild.channels, name="Event Stream")
        event_chat = discord.utils.get(test_guild.channels, name="event-chat")

        online_role = discord.utils.get(interaction.guild.roles, name="Online")
        # Set permissions
        if event_type.value == 0:  # STAGE
            await event_stage.set_permissions(online_role,
                                              connect=enable)
            await event_chat.set_permissions(online_role,
                                             send_messages=enable)
            await interaction.response.send_message(f"Event {event_type.name} mode is now set to '{str(enable)}'")
            pass
        elif event_type.value == 1:  # STREAM
            await event_stream.set_permissions(online_role,
                                               connect=enable)
            await event_chat.set_permissions(online_role,
                                             send_messages=enable)
            await interaction.response.send_message(f"Event {event_type.name} mode is now set to '{str(enable)}'")
            pass
        else:
            await interaction.response.send_message(f"Something broke")
            pass

    # EVENT HOST ONLY
    @app_commands.command(name="emove", description="Moves all members to #Hangout Room VC")
    @app_commands.checks.has_role("Event Host")
    async def eventmove(self, interaction: discord.Interaction):
        test_guild = self.bot.get_guild(int(os.getenv("DEBUG_GUILD_ID")))  # YAY! guild object :catJAM:
        vc_channel = discord.utils.get(test_guild.channels, name="Hangout Room")
        event_stage = discord.utils.get(test_guild.channels, name="Event Stage")
        event_stream = discord.utils.get(test_guild.channels, name="Event Stream")
        for member in event_stream.members:  # Move all #Event Stream to #Hangout Room
            await member.move_to(vc_channel)
        for member in event_stage.members:  # Move all #Event Stage to #Hangout Room
            await member.move_to(vc_channel)
        await interaction.response.send_message(f"Moved all members to <#{vc_channel}>!")

    # EVENT HOST ONLY
    @app_commands.command(name="esize", description="Counts all members in the event")
    @app_commands.checks.has_role("Event Host")
    async def eventsize(self, interaction: discord.Interaction):
        test_guild = self.bot.get_guild(int(os.getenv("DEBUG_GUILD_ID")))  # YAY! guild object :catJAM:
        event_stream = discord.utils.get(test_guild.channels, name="Event Stream")
        # event_stage = discord.utils.get(test_guild.channels, name=" Event Stage")
        await interaction.response.send_message(f"There are {str(len(event_stream.members))} "
                                                f"people in the stream!")

    # ** ONLY
    # @app_commands.default_permissions(moderate_members=True)
    # @app_commands.checks.has_permissions(moderate_members=True)
    # @app_commands.command(name="random", description="Picks a random reacted user from message")
    # async def randomreact(self, interaction: discord.Interaction, msg: discord.InteractionMessage):
    #     users = msg.reactions[0].users().flatten()
    #     print(users)
    #     winner = random.choice(users)
    #     print(winner)
    #     await interaction.response.send_message(f'{winner.mention} is the lucky winner!')


async def setup(bot):
    await bot.add_cog(Events(bot))
