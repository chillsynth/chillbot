# Import discord dependencies
import aiohttp
import discord
import json
from discord.ext.commands import *
from discord.utils import get
# Other dependencies
from lib.helpers import url

COG_NAME = "Moderation"
MODS = (806166163905839154, 835932346099695616)


def is_mod(ctx):
    for role in ctx.author.roles:
        if role.id in MODS:
            return True


def is_dj(ctx):
    for role in ctx.author.roles:
        if role.id == 703643374544093224:
            return True


def name_is_untypable(member):
    test_length = 4
    uname = member.name[0:test_length]
    nick = member.display_name[0:test_length]
    username_untypable = not all(ord(c) < 128 for c in uname)
    nickname_untypable = not all(ord(c) < 128 for c in nick)

    def is_spacey(string):
        spaces = 0
        for c in string:
            if c.isspace():
                spaces += 1
        return (spaces / len(string)) > .33

    are_spacey = is_spacey(uname) and is_spacey(nick)
    return (username_untypable and nickname_untypable) or are_spacey


class CogExt(Cog, name=COG_NAME):
    def __init__(self, bot):
        self.bot = bot

    ## EVENTS

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COG_NAME.lower())
        await self.bot.statchnl.send(f"`{COG_NAME}` cog loaded")

    @Cog.listener()
    async def on_message(self, msg):

        # Define useful shortcuts
        cont = msg.content
        chnl = msg.channel
        author = msg.author
        guild = msg.guild

        if author.bot:
            return

        # Moderation code
        if not is_mod(msg):
            # Code for moderating #new-releases
            if chnl.name == "new-releases":
                if not url.validate(cont):  # If the URL is invalid or there are more than one in the message
                    await msg.delete()  # Then delete the message

            if not is_dj(msg):
                # radio-control moderation
                if chnl.id == 840610850670641222:
                    allowed_cmds = [".np", ".pp10"]
                    if cont not in allowed_cmds and not cont.startswith((">")):
                        await msg.delete()

            # Code for moderating contest submissions
            if chnl.name == "contest-submissions":
                # If the message has text, there is an image, or more than 1 attachment then delete
                if cont != '' or len(msg.attachments) != 1 or msg.attachments[0].height is not None:
                    await msg.delete()

    # # Commands and events for nickname moderation
    # @Cog.listener()
    # async def on_member_join(self, member):
    # 	if name_is_untypable(member):
    # 		await member.edit(nick="rule 11", reason="rule 11")

    # @Cog.listener()
    # async def on_member_update(self, before, after):
    # 	if name_is_untypable(after):
    # 		await after.edit(nick="rule 11", reason="rule 11")

    # Event to restrict access to voice chat text
    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        vcs = [543600804180000788, 850761606408306788, 497637943494836225]
        everyone = member.guild.get_role(488405912659427358)
        chat_chnl = self.bot.get_channel(800792669978361877)
        chnl_open = True

        # if user joined or other update
        try:
            if (after.channel.id in vcs):
                chnl_open = len(after.channel.members) > 0
        # if user left
        except AttributeError:
            if before.channel.id in vcs and len(before.channel.members) == 0:
                chnl_open = False

        await chat_chnl.set_permissions(everyone, send_messages=chnl_open)

    # Automatically grant/remove Supporters role to nitro boosters
    @Cog.listener()
    async def on_member_update(self, before, after):
        # Set common roles
        self.supporter_role = before.guild.get_role(890043225509888040)
        self.booster_role = before.guild.get_role(637750149892014100)
        self.patreon_role = before.guild.get_role(894375740731191316)

        # check if new booster
        if self.booster_role not in before.roles and self.booster_role in after.roles:
            await after.add_roles(self.supporter_role, reason="New Nitro Booster")

        # Patreon subscribers get to keep the supporter role
        if self.patreon_role not in before.roles:
            # if boost expired
            if self.booster_role in before.roles and self.booster_role not in after.roles:
                await after.remove_roles(self.supporter_role, reason="Nitro Boost expired")

    ## COMMANDS

    # Checks if username is untypable
    @command()
    @has_any_role(*MODS)
    async def is_untypable(self, ctx, member: discord.Member):
        await ctx.send(str(name_is_untypable(member)))

    # Command that kicks unregistered scrobblers
    @command()
    @has_any_role(*MODS)
    async def scrobbleprune(self, ctx, reg_users):
        json_raw = ""
        async with aiohttp.ClientSession() as s:
            async with s.get(reg_users) as r:
                json_raw = await r.text()
                reg_users = json.loads(json_raw)
                reg_user_ids = []
                for user in reg_users:
                    reg_user_ids.append(int(user['discordUserID']))
        members = ctx.guild.members
        scrobbler = get(ctx.guild.roles, id=714964255169839125)
        cnt = 0
        for member in members:
            if scrobbler in member.roles and member.id not in reg_user_ids:
                await member.remove_roles(scrobbler, reason="Not registered with Last.fm bot")
                cnt += 1
        await ctx.send(f'Removed {cnt} users from <#714966363114045530>')

    # Removes image posting permissions from specified user
    @command()
    @has_any_role(*MODS)
    async def noimg(self, ctx, member: discord.Member):
        noimg_role = ctx.guild.get_role(854400190425464842)
        va_role = ctx.guild.get_role(637731260520988674)
        en_msg = "Removed image posting permissions"
        dis_msg = "Restored image posting permissions"
        fin_msg = ""

        if noimg_role not in member.roles:
            await member.add_roles(noimg_role, reason=en_msg)
            if va_role in member.roles:
                await member.remove_roles(va_role, reason=en_msg)
            fin_msg = en_msg
        else:
            await member.remove_roles(noimg_role, reason=en_msg)
            fin_msg = dis_msg

        await ctx.send(f"{fin_msg} for user {member.mention}")


def setup(bot):
    bot.add_cog(CogExt(bot))
