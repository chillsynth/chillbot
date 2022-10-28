from discord.ext import commands
from discord import app_commands
import os
import discord


# import random


class Events(commands.Cog):
    def __init__(self, bot):
        # Variables to pre-load
        self.event_stream = None
        self.event_stage = None
        self.event_chat = None
        self.vc_channel = None
        self.online_role = None
        self.event_type = None  # 0 = Stage; 1 = Stream

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
        self.event_stage = self.bot.get_channel(int(os.getenv("EVENT_STAGE_ID")))
        self.event_stream = self.bot.get_channel(int(os.getenv("EVENT_STREAM_ID")))
        self.event_chat = self.bot.get_channel(int(os.getenv("EVENT_CHAT_ID")))

        self.online_role = discord.utils.get(interaction.guild.roles, name="Online")
        # Set permissions
        if event_type.value == 0:  # STAGE
            await self.event_stage.set_permissions(self.online_role,
                                                   connect=enable)
            await self.event_chat.set_permissions(self.online_role,
                                                  send_messages=enable)
            await interaction.response.send_message(f"Event {event_type.name} mode is now set to '{str(enable)}'")
            pass
        elif event_type.value == 1:  # STREAM
            await self.event_stream.set_permissions(self.online_role,
                                                    connect=enable)
            await self.event_chat.set_permissions(self.online_role,
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
        self.vc_channel = self.bot.get_channel(int(os.getenv("PUBLIC_VC_ID")))
        self.event_stage = self.bot.get_channel(int(os.getenv("EVENT_STAGE_ID")))
        self.event_stream = self.bot.get_channel(int(os.getenv("EVENT_STREAM_ID")))
        for member in self.event_stream.members:  # Move all #Event Stream to #Hangout Room
            await member.move_to(self.vc_channel)
        for member in self.event_stage.members:  # Move all #Event Stage to #Hangout Room
            await member.move_to(self.vc_channel)
        await interaction.response.send_message(f"Moved all members to <#{self.vc_channel}>!")

    # EVENT HOST ONLY
    @app_commands.command(name="esize", description="Counts all members in the event")
    @app_commands.checks.has_role("Event Host")
    async def eventsize(self, interaction: discord.Interaction):
        self.event_stream = self.bot.get_channel(int(os.getenv("EVENT_STREAM_ID")))
        self.event_stage = self.bot.get_channel(int(os.getenv("EVENT_STAGE_ID")))
        await interaction.response.send_message(f"There are {str(len(self.event_stream.members))} "
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
