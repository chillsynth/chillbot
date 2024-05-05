from discord.ext import commands
from discord import app_commands
import os
import discord
import logging


class FeedbackQueueView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.INFO)


class Events(commands.Cog):
    def __init__(self, bot):
        # Variables to pre-load
        self.event_stream = None
        self.event_stage = None
        self.event_chat = None
        self.vc_channel = None
        self.online_role = None
        self.event_type = None  # 0 = Stage; 1 = Stream

        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.INFO)

        self.bot = bot

    async def cog_load(self):
        self.logger.info(f"Events.cog: LOADED!")

    # EVENT MODE TOGGLE
    @app_commands.command(name="event", description="Sets Event Mode on and off.")
    @app_commands.checks.has_role("Event Host")
    @app_commands.choices(event_type=[
        discord.app_commands.Choice(name="Stage", value=0),
        discord.app_commands.Choice(name="Stream", value=1)
    ]
    )
    async def event(self, interaction: discord.Interaction,
                    event_type: discord.app_commands.Choice[int],
                    enable: bool):
        await interaction.response.defer()
        self.event_stage = self.bot.get_channel(int(os.getenv("DEV_EVENT_STAGE_ID")))
        self.event_stream = self.bot.get_channel(int(os.getenv("DEV_EVENT_STREAM_ID")))
        self.event_chat = self.bot.get_channel(int(os.getenv("DEV_EVENT_CHAT_ID")))

        self.online_role = discord.utils.get(interaction.guild.roles, name="Online")
        # Set permissions
        if event_type.value == 0:  # STAGE
            await self.event_stage.set_permissions(self.online_role, connect=enable)
            await self.event_chat.set_permissions(self.online_role, send_messages=enable)
            await interaction.followup.send(content=f"Event {event_type.name} mode is now set to '{str(enable)}'")

        # STREAM
        elif event_type.value == 1:
            await self.event_stream.set_permissions(self.online_role, connect=enable)
            await self.event_chat.set_permissions(self.online_role, send_messages=enable)
            await interaction.followup.send(content=f"Event {event_type.name} mode is now set to '{str(enable)}'")
            pass

        # I have no idea what would cause this so covering for the worst scenario
        else:
            await interaction.followup.send(content=f"Something broke in [event] logic.")
            pass

    # MOVE EVENT MEMBERS TO VC
    # TODO: Add option to move to any other VC (ideal for Stage <-> Stream)
    @app_commands.command(name="emove", description="Moves all members to #Hangout Room VC")
    @app_commands.checks.has_role("Event Host")
    async def eventmove(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.vc_channel = self.bot.get_channel(int(os.getenv("DEV_PUBLIC_VC_ID")))
        self.event_stage = self.bot.get_channel(int(os.getenv("DEV_EVENT_STAGE_ID")))
        self.event_stream = self.bot.get_channel(int(os.getenv("DEV_EVENT_STREAM_ID")))
        for member in self.event_stream.members:  # Move all #Event Stream to #Hangout Room
            await member.move_to(self.vc_channel)
        for member in self.event_stage.members:  # Move all #Event Stage to #Hangout Room
            await member.move_to(self.vc_channel)
        await interaction.followup.send(content=f"Moved all members to <#{self.vc_channel}>!")

    # GET EVENT MEMBER COUNT
    @app_commands.command(name="ecount", description="Counts all members in the event")
    @app_commands.checks.has_role("Event Host")
    async def eventsize(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.event_stream = self.bot.get_channel(int(os.getenv("DEV_EVENT_STREAM_ID")))
        self.event_stage = self.bot.get_channel(int(os.getenv("DEV_EVENT_STAGE_ID")))
        await interaction.followup.send(content=f"There are {str(len(self.event_stream.members))} "
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
