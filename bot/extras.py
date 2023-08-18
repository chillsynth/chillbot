import re
import os
import logging
import motor.motor_asyncio
import discord
from discord.ext import commands, tasks
from discord import app_commands  # - USE FOR MANUAL
from datetime import datetime, timedelta
from time import mktime
import requests


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
            f"Cooldown active! Please retry <t:{int(mktime(datetime(*cooldown_time_tuple).timetuple()))}:R>",
            delete_after=error.retry_after
        )

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
            async for result in self.db.youtube_uploads.find(key):
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
                await self.db.youtube_uploads.update_one(db_filter, upload_updated_value)

                # Send new upload embed to #youtube-feed
                self.logger.debug(f"New upload for [{upload_channel}] has been found! Posting to #youtube-feed.")
                youtube_webhook = discord.SyncWebhook.from_url(os.getenv("DEV_YOUTUBE_URL"))
                youtube_webhook.send(f"{upload_title}: https://youtube.com/watch?v={url_id}")

            channel_counter += 1

        self.logger.info(f"Extras.cog: YouTube Scan complete!")
        # self.logger.info(f"Extras.cog: /scan by {interaction.user.id} complete!") - USE FOR MANUAL
        # await interaction.edit_original_response(content="Done!") - USE FOR MANUAL

    @tasks.loop(minutes=15)  # RATE LIMIT IS 10 minutes ish
    async def resonance_update(self):
        # Retrieve leaderboard DB
        stats_out = None
        async for result in self.db.stats.find():
            stats_out = result

        the_guild: discord.Guild = await self.bot.fetch_guild(int(os.getenv("DEV_GUILD_ID")))
        resonance_channel = await the_guild.fetch_channel(int(os.getenv("DEV_RESONANCE_ID")))

        await resonance_channel.edit(name=f"Resonances: {stats_out['global_resonance_count']}")  # +1 ????
        self.logger.info(f"Extras.cog: Resonance Update complete!")

    # @app_commands.checks.cooldown(1, 120.0, key=None)  # TODO: RE-APPLY THE COOLDOWN!!
    @app_commands.command(name="leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        # Search DB record
        search_result = None
        async for result in self.db.stats.find({}):
            # print(f"Found {new.name}#{new.discriminator} under: ObjectID:{result['_id']}")  # DEBUG
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

        await interaction.response.send_message(embed=leaderboard_embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if "resonance" in message.content.lower():
            self.logger.info(f"Reacted 'resonance' to message: {message.jump_url}")
            await message.add_reaction("<:resonanceDEV:1020142646787837992>")  # TODO: REPLACE LIVE EMOJI
            # <:resonance:699652237135183982> Actual emoji_ID when integrated
            # <:resonanceDEV:1020142646787837992> TEST Emoji

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
            await message.add_reaction("<:egemDEV:1062784474351403068>")  # TODO: REPLACE LIVE EMOJI
            # <:egem:852516812423430144> Actual emoji_ID when integrated
            # <:egemDEV:1062784474351403068> TEST Emoji

        if message.stickers:  # Message contains a sticker
            if message.stickers[0].name == "Live Albert Reaction":
                await message.channel.send("<@615822182454657025>")


async def setup(bot):
    await bot.add_cog(Extras(bot))
