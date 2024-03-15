from discord.ext import commands
from discord import app_commands
import discord
import motor.motor_asyncio
import os
import logging


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # DB Setup
        self.client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("DEV_MONGO_URI"))
        self.db = self.client["_server"]

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

    # * ONLY - ONE TIME USE ONLY!!!!!
    @commands.is_owner()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.command(name="resetdb", description="Updates bot user DB - DO NOT USE!!")
    async def reset_db(self, interaction: discord.Interaction):
        await interaction.response.defer()

        self.db = self.client["_server"]

        '''
            RESET members
        '''

        member_list = []
        bot_list = []
        await self.db.members.delete_many({})  # DELETE DB
        async for member in interaction.guild.fetch_members(limit=None):
            member_list.append(member)
            self.logger.debug(f"Admin.cog: Processing: {member} into DB")
            if member.bot is not True:  # Check for bot and skip if True
                print(member)
                if member.premium_since is not None:  # Check boosting status
                    member_is_boosting = True
                else:
                    member_is_boosting = False

                # Create new entry in DB
                await self.db.members.insert_one(
                    {
                        "discord_username": str(f"{member.global_name}"),
                        "discord_user_ID": int(member.id),
                        "discord_creation_date": int(member.created_at.timestamp()),  # strftime("%d/%m/%Y @ %H:%M:%S")
                        "server_nickname": str(f"{member.nick}"),
                        "server_join_date": int(member.joined_at.timestamp()),
                        "server_leave_date": None,  # Epoch will be filled if left server
                        "server_resonance_count": 0,
                        "is_booster": bool(member_is_boosting),
                        "past_usernames": {
                            "username": ["", "", "", "", ""],
                            "user_date_changed": ["", "", "", "", ""]
                        },
                        "past_nicknames": {
                            "nickname": ["", "", "", "", ""],
                            "nick_date_changed": ["", "", "", "", ""]
                        },
                        "soundcloud_url": "",
                        "bandcamp_url": "",
                        "other_url": ""
                    }
                )
            elif member.bot is True:
                bot_list.append(member)
                self.logger.debug(f"Admin.cog: Skipping bot: {member}")
            else:
                print("Something broke!")
                self.logger.error(f"Admin.cog: Unknown error fetching member in reset_db()")

        print(str(f"{member_list}\n{bot_list}"))

        '''
            RESET stats
        '''

        await self.db.stats.delete_many({})  # DELETE DB

        await self.db.stats.insert_one(
            {
                "global_resonance_count": 0,
                "leaderboard": [
                    [0, 0],
                    [0, 0],
                    [0, 0],
                    [0, 0],
                    [0, 0],
                ]
            }
        )

        '''
            RESET youtube_uploads
        '''

        await self.db.youtube_uploads.delete_many({})  # DELETE DB - Replaced on next scan

        '''
            RESET _events.information
        '''

        await self.client["_events"].information.delete_many({})  # Delete DB

        await self.client["_events"].information.insert_one(
            {
                "message_ID": 0,
                "channel_ID": 0,
                "last_user_ID": 0,
                "slots": 0,
                "submission_locator": "here i am",
            }
        )

        '''
            RESET _events.current_submissions && _events.feedback_queue
        '''

        await self.client["_events"].current_submissions.delete_many({})  # Delete DB
        await self.client["_events"].feedback_queue.delete_many({})  # Delete DB

        await interaction.edit_original_response(content=f"Done! :)")
        self.logger.warning(f"Admin.cog: All DB's reset ! ! !")

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
