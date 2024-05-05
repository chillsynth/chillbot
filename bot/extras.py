import re
import os
import logging
import motor.motor_asyncio
import discord
from discord.ext import commands, tasks
from discord import app_commands  # - USE FOR MANUAL
from datetime import datetime, timedelta
from time import mktime
import feedparser
import pytz


class Extras(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # DB Setup
        self.client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("DEV_MONGO_URI"))
        self.db = self.client["_server"]

        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.INFO)

    async def cog_load(self):
        self.logger.info(f"Extras.cog: LOADED!")
        self.logger.info(f"Extras.cog: YouTube Scanner started")
        self.youtube_scan.start()
        self.resonance_update.start()

    async def cog_unload(self):
        # Cancel the task loops when unloaded
        self.youtube_scan.cancel()
        self.resonance_update.cancel()

    async def cog_app_command_error(self,
                                    interaction: discord.Interaction,
                                    error: app_commands.errors.CommandOnCooldown) -> None:
        cooldown_time = datetime.now() + timedelta(seconds=error.retry_after)
        cooldown_time_tuple = (cooldown_time.year, cooldown_time.month, cooldown_time.day,
                               cooldown_time.hour, cooldown_time.minute, cooldown_time.second)
        print(cooldown_time)
        await interaction.response.send_message(
            content=f"Cooldown active! Please retry <t:{int(mktime(datetime(*cooldown_time_tuple).timetuple()))}:R>",
            delete_after=error.retry_after
        )

    @tasks.loop(minutes=10)
    async def youtube_scan(self):
        channels = [
                "https://www.youtube.com/feeds/videos.xml?channel_id=UCPzWlhG7QM56Y8MYB3qMVnQ",  # ELECTRONIC GEMS
                "https://www.youtube.com/feeds/videos.xml?channel_id=UCjPLBJtP7zq16YVcT3_gmkg",  # POLYCHORA
                "https://www.youtube.com/feeds/videos.xml?channel_id=UCzIGoCCmSvgJgaxFFOOBJdQ",  # Definition of Chill.
                "https://www.youtube.com/feeds/videos.xml?channel_id=UCwoTj-pZgZZ8DInOXSSLMmA",  # Odysseus
                "https://www.youtube.com/feeds/videos.xml?channel_id=UCHSv5KYYBSlOS340sdHK2ew",  # DFTI
                "https://www.youtube.com/feeds/videos.xml?channel_id=UCmJHkrvlDlFws5Rw1AYUWMQ"   # Hurleybird
        ]

        for channel_url in channels:
            rss_data = feedparser.parse(channel_url)
            upload_channel = rss_data.feed.title
            upload_title = rss_data.entries[0].title
            upload_url = rss_data.entries[0].link
            upload_time = rss_data.entries[0].published

            upload_time = datetime.fromisoformat(upload_time)
            now_time = datetime.utcnow().replace(tzinfo=pytz.utc).replace(microsecond=0)
            time_diff: timedelta = now_time - upload_time
            self.logger.info(f"Time diff: {time_diff}")

            if time_diff.days == 0:
                if time_diff.seconds >= 600:  # 600 = 10 minutes per scan - OLD UPLOAD
                    self.logger.debug(f"{upload_channel}: No new posts.")
                elif time_diff.seconds < 600:  # NEW UPLOAD - YIPPEE!  --  Send new upload embed to #youtube-feed
                    self.logger.debug(f"New upload for [{upload_channel}] has been found! Posting to #youtube-feed.")

                    youtube_webhook = discord.SyncWebhook.from_url(os.getenv("DEV_YOUTUBE_URL"))
                    youtube_webhook.send(f"{upload_title}: {upload_url}")

        self.logger.debug(f"Extras.cog: YouTube Scan complete!")

    @app_commands.command(name="scan", description="Scan the YouTube channels and output details to console.")
    async def manual_youtube_scan(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        await self.youtube_scan()
        self.logger.info(f"Extras.cog: /scan by {interaction.user.id} complete!")
        await interaction.edit_original_response(content="Done!")

    @tasks.loop(minutes=20)  # RATE LIMIT IS 10 minutes ish
    async def resonance_update(self):
        # Retrieve leaderboard DB
        stats_out = None
        async for result in self.db.stats.find():
            stats_out = result

        the_guild: discord.Guild = await self.bot.fetch_guild(int(os.getenv("DEV_GUILD_ID")))
        resonance_channel = await the_guild.fetch_channel(int(os.getenv("DEV_RESONANCE_ID")))

        await resonance_channel.edit(name=f"Resonances: {stats_out['global_resonance_count']}")  # +1 ????
        self.logger.info(f"Extras.cog: Resonance Update complete!")

    @app_commands.checks.cooldown(1, 120.0, key=None)
    @app_commands.command(name="leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()
        # Search DB record
        search_result = None
        async for result in self.db.stats.find({}):
            # print(f"Found {new.global_name} under: ObjectID:{result['_id']}")  # DEBUG
            print(result)
            search_result = result

        leaderboard_embed = discord.Embed(
            title="Resonance Leaderboard",
            colour=0x8080a2,
            timestamp=datetime.now()
        )

        leaderboard_embed.add_field(
            name="1.",
            value=f"<@{search_result['leaderboard'][0][0]}> --- x {search_result['leaderboard'][0][1]}",
            inline=False
        )
        leaderboard_embed.add_field(
            name="2.",
            value=f"<@{search_result['leaderboard'][1][0]}> --- x {search_result['leaderboard'][1][1]}",
            inline=False
        )
        leaderboard_embed.add_field(
            name="3.",
            value=f"<@{search_result['leaderboard'][2][0]}> --- x {search_result['leaderboard'][2][1]}",
            inline=False
        )
        leaderboard_embed.add_field(
            name="4.",
            value=f"<@{search_result['leaderboard'][3][0]}> --- x {search_result['leaderboard'][3][1]}",
            inline=False
        )
        leaderboard_embed.add_field(
            name="5.",
            value=f"<@{search_result['leaderboard'][4][0]}> --- x {search_result['leaderboard'][4][1]}",
            inline=False
        )

        leaderboard_embed.set_image(url="https://cdn.discordapp.com/emojis/699652237135183982.webp")
        leaderboard_embed.set_footer(text="Last Updated")

        await interaction.followup.send(embed=leaderboard_embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if "resonance" in message.content.lower():
            self.logger.info(f"Reacted 'resonance' to message: {message.jump_url}")
            await message.add_reaction(os.getenv("DEV_EMOJI_RESONANCE"))

            # Retrieve leaderboard DB
            current_stats = None
            async for result in self.db.stats.find():
                current_stats = result

            await self.db.members.update_one(
                {"discord_user_ID": message.author.id},
                {"$inc": {"server_resonance_count": 1}}
            )

            await self.db.stats.update_one(
                {"global_resonance_count": current_stats["global_resonance_count"]},
                {"$inc": {"global_resonance_count": 1}}
            )

            current_top_5 = self.db.members.find().sort("server_resonance_count", -1).limit(5)
            list_cur = await current_top_5.to_list(length=5)
            resonance_leaderboard = []
            for i in range(0, 5):
                resonance_leaderboard.append([list_cur[i]['discord_user_ID'], list_cur[i]['server_resonance_count']])

            await self.db.stats.update_one(
                {},
                {"$set": {"leaderboard": resonance_leaderboard}}
            )

        if "electronic gem" in message.content.lower():
            self.logger.info(f"Reacted 'egem' to message: {message.jump_url}")
            await message.add_reaction(os.getenv("DEV_EMOJI_EGEM"))

        if message.stickers:  # Message contains a sticker
            if message.stickers[0].name == "Live Albert Reaction":
                await message.channel.send("<@615822182454657025>")


async def setup(bot):
    await bot.add_cog(Extras(bot))
