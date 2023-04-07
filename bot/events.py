import typing

from discord.ext import commands
from discord import app_commands
import os
import discord
import pymongo


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

        # DB Setup
        self.client = pymongo.MongoClient(os.getenv("mongo_dev_uri"))
        self.db = self.client["_events"]

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

    @commands.Cog.listener()
    async def on_thread_create(self, thread):
        if thread.parent.type == discord.ChannelType.forum:  # Check if thread is in FORUM channel
            new_tag = discord.utils.get(thread.parent.available_tags, name="New")
            await thread.add_tags(new_tag)

    @commands.Cog.listener()
    async def on_thread_delete(self, name):
        print(name)

    # TRACK SUBMIT
    @app_commands.command(name="submit", description="Submit your track for the Feedback Stream")
    async def submit(self, interaction: discord.Interaction):
        print("FINISH THIS")

    # TODO
    #   Feedback queue embed system
    #   User discord GET user profile pic for embed
    #   SoundCloud link command
    #   Booster Check and queue system

    # EVENT HOST ONLY
    @app_commands.command(name="fb", description="Feedback Stream commands")
    @app_commands.checks.has_role("Event Host")
    @app_commands.choices(
        option=[
            discord.app_commands.Choice(name="Add", value=0),
            discord.app_commands.Choice(name="Remove", value=1),
            discord.app_commands.Choice(name="Decline", value=2),
            discord.app_commands.Choice(name="Review", value=3)
        ]
    )
    async def fb(self, interaction: discord.Interaction,
                 option: discord.app_commands.Choice[int],
                 reason: typing.Optional[str]):
        # ADD TRACK TO QUEUE
        if option.value == 0:
            new_tag = discord.utils.get(interaction.channel.parent.available_tags, name="Added")
            await interaction.channel.edit(applied_tags=[new_tag])

            # Submit new DB record with submission data
            self.db.feedback_queue.insert_one(
                {
                    "track_title": str(interaction.channel.name),
                    "track_artist": str(interaction.channel.name),
                    "submission_user_ID": int(interaction.channel.owner.id),
                    "thread_ID": int(interaction.channel.id)
                }
            )

            print(f"Added record for {interaction.channel.name}")  # Send to system logs

            feedback_queue_thread = discord.utils.get(interaction.guild.threads, name="Feedback Stream™ Queue")
            print(feedback_queue_thread)

            # https://discohook.org/?data=eyJtZXNzYWdlcyI6W3siZGF0YSI6eyJjb250ZW50IjpudWxsLCJlbWJlZHMiOlt7ImNvbG9yIjoxNjc0NDgzMCwiZmllbGRzIjpbeyJuYW1lIjoiQ1VSUkVOVExZIFBMQVlJTkciLCJ2YWx1ZSI6IlRlc3QgVHJhY2sgLSBIdXJsZXliaXJkIiwiaW5saW5lIjp0cnVlfSx7Im5hbWUiOiJTdWJtaXR0ZWQgQnkiLCJ2YWx1ZSI6IlVzZXJuYW1lIzAwMDEifV0sImZvb3RlciI6eyJ0ZXh0IjoiTGFzdCBVcGRhdGVkIn0sInRpbWVzdGFtcCI6IjIwMjMtMDEtMzBUMjM6MDE6MDAuMDAwWiIsInRodW1ibmFpbCI6eyJ1cmwiOiJodHRwczovL2Nkbi5kaXNjb3JkYXBwLmNvbS9hdmF0YXJzLzM2MDg4MjkwMzkxMzIwMTY3NS9hX2I1YTYzMGVmYmJhMmNhMTY0NjRkMTRjYTQ4MmRjNWE3LmdpZj9zaXplPTEwMjQifX0seyJ0aXRsZSI6IlVQIE5FWFQiLCJjb2xvciI6MzQ5NzA4MywiZmllbGRzIjpbeyJuYW1lIjoiPiAxIiwidmFsdWUiOiJ0cmFjayBuYW1lIC0gYXJ0aXN0IG5hbWUiLCJpbmxpbmUiOnRydWV9LHsibmFtZSI6Ij4gMiIsInZhbHVlIjoidHJhY2sgbmFtZSAtIGFydGlzdCBuYW1lIiwiaW5saW5lIjp0cnVlfSx7Im5hbWUiOiI-IDMiLCJ2YWx1ZSI6InRyYWNrIG5hbWUgLSBhcnRpc3QgbmFtZSIsImlubGluZSI6dHJ1ZX0seyJuYW1lIjoiPiA0IiwidmFsdWUiOiJ0cmFjayBuYW1lIC0gYXJ0aXN0IG5hbWUiLCJpbmxpbmUiOnRydWV9LHsibmFtZSI6Ij4gNSIsInZhbHVlIjoidHJhY2sgbmFtZSAtIGFydGlzdCBuYW1lIiwiaW5saW5lIjp0cnVlfSx7Im5hbWUiOiI-IDYiLCJ2YWx1ZSI6InRyYWNrIG5hbWUgLSBhcnRpc3QgbmFtZSIsImlubGluZSI6dHJ1ZX0seyJuYW1lIjoiPiA3IiwidmFsdWUiOiJ0cmFjayBuYW1lIC0gYXJ0aXN0IG5hbWUiLCJpbmxpbmUiOnRydWV9LHsibmFtZSI6Ij4gOCIsInZhbHVlIjoidHJhY2sgbmFtZSAtIGFydGlzdCBuYW1lIiwiaW5saW5lIjp0cnVlfSx7Im5hbWUiOiI-IDkiLCJ2YWx1ZSI6InRyYWNrIG5hbWUgLSBhcnRpc3QgbmFtZSIsImlubGluZSI6dHJ1ZX1dLCJmb290ZXIiOnsidGV4dCI6Ikxhc3QgVXBkYXRlZCJ9LCJ0aW1lc3RhbXAiOiIyMDIzLTAxLTMwVDIzOjAxOjAwLjAwMFoifV0sInVzZXJuYW1lIjoiRmVlZGJhY2sgU3RyZWFt4oSiIFF1ZXVlIiwiYXR0YWNobWVudHMiOltdfX1dfQ

            await feedback_queue_thread.send(content="Test1")
            # 1 - Test Track by Hurleybird
            await interaction.response.send_message(
                f"Added {interaction.channel.name} to the Feedback Stream™ Queue!")

        # REMOVE TRACK FROM QUEUE
        elif option.value == 1:
            new_tag = discord.utils.get(interaction.channel.parent.available_tags, name="New")
            await interaction.channel.edit(applied_tags=[new_tag])

            # Locate submission's ObjectID and delete record in DB
            channel = interaction.channel.id
            key = {"thread_ID": channel}

            # Search and delete DB record
            for result in self.db.feedback_queue.find(key):
                delete_key = {"_id": result["_id"]}
                self.db.feedback_queue.delete_one(delete_key)
                print(f"Deleted record for {interaction.channel.name} ObjectID:{result['_id']}")  # Send to system logs

            await interaction.response.send_message(
                f"Removed {interaction.channel.name} from the queue.")

        # DECLINE SUBMISSION WITH REASON
        elif option.value == 2:
            new_tag = discord.utils.get(interaction.channel.parent.available_tags, name="Declined")
            await interaction.channel.edit(applied_tags=[new_tag])

            # Locate submission's ObjectID and delete record in DB
            channel = interaction.channel.id
            key = {"thread_ID": channel}

            for result in self.db.feedback_queue.find(key):
                delete_key = {"_id": result["_id"]}
                self.db.feedback_queue.delete_one(delete_key)
                print(f"Deleted record for {interaction.channel.name} ObjectID:{result['_id']}")  # Send to system logs

            await interaction.response.send_message(
                f"Declined submission for reason: {reason}")

        # NEEDS REVIEW WITH REASON
        elif option.value == 3:
            new_tag = discord.utils.get(interaction.channel.parent.available_tags, name="Needs Review")
            await interaction.channel.edit(applied_tags=[new_tag])

            # Locate submission's ObjectID and delete record in DB
            channel = interaction.channel.id
            key = {"thread_ID": channel}

            for result in self.db.feedback_queue.find(key):
                delete_key = {"_id": result["_id"]}
                self.db.feedback_queue.delete_one(delete_key)
                print(f"Deleted record for {interaction.channel.name} ObjectID:{result['_id']}")  # Send to system logs

            await interaction.response.send_message(
                f"Needs review for reason: {reason}")

        else:
            await interaction.response.send_message(f"Something broke in [fb] logic.")

    # EVENT MODE TOGGLE
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

        # STREAM
        elif event_type.value == 1:
            await self.event_stream.set_permissions(self.online_role,
                                                    connect=enable)
            await self.event_chat.set_permissions(self.online_role,
                                                  send_messages=enable)
            await interaction.response.send_message(f"Event {event_type.name} mode is now set to '{str(enable)}'")
            pass

        # I have no idea what would cause this so covering for the worst scenario
        else:
            await interaction.response.send_message(f"Something broke in [event] logic.")
            pass

    # MOVE EVENT MEMBERS TO VC
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

    # GET EVENT MEMBER COUNT
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
