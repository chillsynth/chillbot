from discord.ext import commands
from discord import app_commands
import discord
import pymongo
import os
from datetime import *


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # DB Setup
        self.client = pymongo.MongoClient(os.getenv("mongo_dev_uri"))
        self.db = self.client["_server"]

    async def cog_load(self):
        print(f"`Admin` cog loaded")

    # * ONLY - ONE TIME USE ONLY!!!!!
    @app_commands.command(name="resetdb", description="Updates bot DB - DO NOT USE!!")
    @app_commands.checks.has_permissions(administrator=True)
    async def reset_db(self, interaction: discord.Interaction):
        async for member in interaction.guild.fetch_members(limit=None):
            print(member)

            if member.bot is not True:  # Check for bot and skip if True
                if member.premium_since is not None:  # Check boosting status
                    member_is_boosting = True
                else:
                    member_is_boosting = False

                # Create new entry in DB
                self.db.members.insert_one(
                    {
                        "discord_username": str(f"{member.name}#{member.discriminator}"),
                        "discord_user_ID": int(member.id),
                        "discord_creation_date": int(member.created_at.timestamp()),  # strftime("%d/%m/%Y @ %H:%M:%S")
                        "server_nickname": str(f"{member.nick}"),
                        "server_join_date": int(member.joined_at.timestamp()),
                        "server_leave_date": None,  # Epoch will be filled if left server
                        "is_booster": bool(member_is_boosting),
                        "past_usernames": {
                            "username": ["", "", "", "", ""],
                            "user_date_changed": ["", "", "", "", ""]
                        },
                        "past_nicknames": {
                            "nickname": ["", "", "", "", ""],
                            "nick_name_changed": ["", "", "", "", ""]
                        }
                    }
                )
            elif member.bot is True:
                print("Bot! Skipping...")
            else:
                print("Something broke!")

        await interaction.response.send_message(f"Done! :)")


async def setup(bot):
    await bot.add_cog(Admin(bot))
