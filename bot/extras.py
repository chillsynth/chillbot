import re
import os
import logging
import pymongo
import discord
from discord.ext import commands, tasks
# from discord import app_commands - USE FOR MANUAL
from datetime import datetime
import requests


class Extras(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # DB Setup
        self.client = pymongo.MongoClient(os.getenv("mongo_dev_uri"))
        self.db = self.client["_server"]

        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.INFO)

    async def cog_load(self):
        self.logger.info(f"Extras.cog: LOADED!")
        self.logger.info(f"Extras.cog: YouTube Scanner started")
        self.youtube_scan.start()

    async def cog_unload(self):
        self.youtube_scan.cancel()  # Cancel the task loop when unloaded

    # YOUTUBE SCANNER
    # MANUAL @app_commands.command(name="scan", description="Scan the YouTube channels and output details to console.")
    @tasks.loop(minutes=10)
    async def youtube_scan(self):  # , interaction: discord.Interaction): - USE FOR MANUAL
        # await interaction.response.defer(thinking=True) - USE FOR MANUAL

        channels = {
            "channel_URLs": [
                "https://www.youtube.com/@ElectronicGems",
                "https://www.youtube.com/@Polychora",
                "https://www.youtube.com/@DefinitionofChill",
                "https://www.youtube.com/@OdysseusOfficial",
                "https://www.youtube.com/@disconnectedfromtheinterwe9157"
            ],
            "channel_names": [
                "Electronic Gems",
                "Polychora",
                "Definition of Chill.",
                "Odysseus",
                "disconnected from the interweb"
            ]
        }

        cookies_dict = {"SOCS": "CAESEwgDEgk0ODE3Nzk3MjQaAmVuIAEaBgiA_LyaBg"}  # Cookie for "accepting" cookie wall

        channel_counter = 0
        for current_channel in channels["channel_URLs"]:
            html = requests.get(current_channel + "/videos", cookies=cookies_dict)
            html_result = html.content.decode("utf-8")

            s_idx = html_result.find("accessibilityData") + 29  # Remove prefix
            e_idx = html_result.find("descriptionSnippet") - 6  # Remove suffix

            url_s_idx = html_result.find("videoRenderer") + 27  # Remove prefix
            url_e_idx = url_s_idx + 11  # Extract only the videoID
            url_id = html_result[url_s_idx:url_e_idx]

            full_upload_data = html_result[s_idx:e_idx]

            channel_to_regex = channels["channel_names"][channel_counter]

            # Extract details using regex
            upload_channel = re.search(r'(?<=by\s)' + channel_to_regex, full_upload_data)[0].rstrip(" ")
            upload_title = re.findall(rf"^.*?(?=by {channel_to_regex})", full_upload_data)[0].strip()
            upload_title = bytes(upload_title, 'utf-8').decode('unicode_escape')  # Parse any Unicodes: \uu0026 = &

            # Search DB record for current upload document
            key = {"youtube_channel_name": upload_channel}
            search_result = None
            for result in self.db.youtube_uploads.find(key):
                search_result = result
                # self.logger.debug(f"Extras.cog: Found {upload_channel} under: ObjectID:{result['_id']}")

            if search_result is None:  # No existing record found - DB or lookup error?
                self.logger.critical(f"[!] Extras.cog: No existing record for [{upload_channel}] found [!]")

            elif search_result["upload_title"] == upload_title:  # Both upload titles match - no change
                self.logger.debug(f"Current upload for [{upload_channel}] matches existing record - No Change.")

            elif upload_title != search_result["upload_title"]:  # Existing upload title outdated - update record
                upload_updated_value = {
                    "$set": {
                        "youtube_channel_name": str(f"{upload_channel}"),
                        "upload_title": str(f"{upload_title}"),
                        "last_updated": float(f"{datetime.now().timestamp()}"),
                    }
                }

                db_filter = {"youtube_channel_name": upload_channel}  # Filter by old upload title
                self.db.youtube_uploads.update_one(db_filter, upload_updated_value)

                # Send new upload embed to #youtube-feed
                self.logger.debug(f"New upload for [{upload_channel}] has been found! Posting to #youtube-feed.")
                youtube_webhook = discord.SyncWebhook.from_url(os.getenv("DEV!_YOUTUBE_URL"))  # TODO: REPLACE LIVE ENV
                youtube_webhook.send(f"{upload_title}: https://youtube.com/watch?v={url_id}")

            channel_counter += 1

        self.logger.info(f"Extras.cog: YouTube Scan complete!")
        # self.logger.info(f"Extras.cog: /scan by {interaction.user.id} complete!") - USE FOR MANUAL
        # await interaction.edit_original_response(content="Done!") - USE FOR MANUAL

    @commands.Cog.listener()
    async def on_message(self, message):
        if "resonance" in message.content.lower():
            self.logger.info(f"Reacted 'resonance' to message: {message.jump_url}")
            await message.add_reaction("<:resonanceDEV:1020142646787837992>")  # TODO: SWITCH EMOJI ID RESONANCE
            # <:resonance:699652237135183982> Actual emoji_ID when integrated
            # <:resonanceDEV:1020142646787837992> TEST Emoji
        if "electronic gem" in message.content.lower():
            self.logger.info(f"Reacted 'egem' to message: {message.jump_url}")
            await message.add_reaction("<:egemDEV:1062784474351403068>")  # TODO: SWITCH EMOJI ID ELECTRONIC GEMS
            # <:egem:852516812423430144> Actual emoji_ID when integrated
            # <:egemDEV:1062784474351403068> TEST Emoji


async def setup(bot):
    await bot.add_cog(Extras(bot))
