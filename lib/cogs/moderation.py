# Import discord dependencies
from discord import PermissionOverwrite
from discord.ext.commands import *
from discord.utils import get
import discord, aiohttp, json

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
				spaces+=1
		return (spaces/len(string)) > .33
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

		#Define useful shortcuts
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
				if not url.validate(cont): # If the URL is invalid or there are more than one in the message
					await msg.delete()     # Then delete the message

			#if not is_dj(msg):
			#	# radio-control moderation
			#	if chnl.id == 840610850670641222:
			#		allowed_cmds = [".np", ".pp10", "-q", "-queue", "-np"]
			#		if cont not in allowed_cmds and not cont.startswith(("-p", "-play")):
			#			await msg.delete()


			# Code for moderating contest submissions
			if chnl.name == "contest-submissions":
				# If the message has text, there is an image, or more than 1 attachment then delete
				if cont != '' or len(msg.attachments) != 1 or msg.attachments[0].height is not None:
						await msg.delete()

	# Commands and events for nickname moderation
	@Cog.listener()
	async def on_member_join(self, member):
		if name_is_untypable(member):
			await member.edit(nick="rule 11", reason="rule 11")

	@Cog.listener()
	async def on_member_update(self, before, after):
		if name_is_untypable(after):
			await after.edit(nick="rule 11", reason="rule 11")

	

	# Event to restrict access to voice chat text
	@Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		vcs = [543600804180000788, 497637943494836225, 836019956377845790]
		chat_chnl = self.bot.get_channel(800792669978361877)
		blank_chnl = self.bot.get_channel(619320260591484943)
		before_channel = before.channel
		after_channel = after.channel

		if before_channel == None:
			before_channel = blank_chnl
		if after_channel == None:
			after_channel = blank_chnl
		if (before_channel.id not in vcs) and (after_channel.id in vcs):
			await chat_chnl.set_permissions(member, send_messages=True)
		if (before_channel.id in vcs) and (after_channel.id not in vcs):
			await chat_chnl.set_permissions(member, overwrite=None)


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

	

def setup(bot):
	bot.add_cog(CogExt(bot))
