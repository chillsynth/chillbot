import os
import logging
import discord
from discord.ext import commands, tasks
from discord import app_commands  # - USE FOR MANUAL
from datetime import datetime, timedelta, timezone
import feedparser
import pytz


class Extras(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.INFO)

    async def cog_load(self):
        self.logger.info(f"Extras.cog: LOADED!")
        self.logger.info(f"Extras.cog: YouTube Scanner started")
        self.youtube_scan.start()

    async def cog_unload(self):
        # Cancel the task loops when unloaded
        self.youtube_scan.cancel()

    @tasks.loop(minutes=20)
    async def youtube_scan(self):
        channels = [
                "https://www.youtube.com/feeds/videos.xml?channel_id=UCPzWlhG7QM56Y8MYB3qMVnQ",  # ELECTRONIC GEMS
                "https://www.youtube.com/feeds/videos.xml?channel_id=UCjPLBJtP7zq16YVcT3_gmkg",  # POLYCHORA
                "https://www.youtube.com/feeds/videos.xml?channel_id=UCzIGoCCmSvgJgaxFFOOBJdQ",  # Definition of Chill.
                "https://www.youtube.com/feeds/videos.xml?channel_id=UCwoTj-pZgZZ8DInOXSSLMmA",  # Odysseus
                "https://www.youtube.com/feeds/videos.xml?channel_id=UCHSv5KYYBSlOS340sdHK2ew"   # DFTI
                # "https://www.youtube.com/feeds/videos.xml?channel_id=UCmJHkrvlDlFws5Rw1AYUWMQ"   # Hurleybird
        ]

        for channel_url in channels:
            rss_data = feedparser.parse(channel_url)
            upload_channel = rss_data.feed.title
            upload_title = rss_data.entries[0].title
            upload_url = rss_data.entries[0].link
            upload_time = rss_data.entries[0].published

            upload_time = datetime.fromisoformat(upload_time)
            now_time = datetime.now(timezone.utc).replace(tzinfo=pytz.utc).replace(microsecond=0)
            time_diff: timedelta = now_time - upload_time
            self.logger.info(f"Time diff: {time_diff}")

            if time_diff.days == 0:
                if time_diff.seconds >= 1200:  # 1200 = 20 minutes per scan - OLD UPLOAD
                    self.logger.debug(f"{upload_channel}: No new posts.")
                elif time_diff.seconds < 1200:  # NEW UPLOAD - YIPPEE!  --  Send new upload embed to #youtube-feed
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

    @commands.Cog.listener()
    async def on_message(self, message):
        if "resonance" in message.content.lower():
            self.logger.info(f"Reacted 'resonance' to message: {message.jump_url}")
            await message.add_reaction(os.getenv("DEV_EMOJI_RESONANCE"))

        if "electronic gem" in message.content.lower():
            self.logger.info(f"Reacted 'egem' to message: {message.jump_url}")
            await message.add_reaction(os.getenv("DEV_EMOJI_EGEM"))

        if message.stickers:  # Message contains a sticker
            if message.stickers[0].name == "Live Albert Reaction":
                await message.channel.send("<@615822182454657025>")


async def setup(bot):
    await bot.add_cog(Extras(bot))
