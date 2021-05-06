# Import discord dependencies
from discord import PermissionOverwrite
from discord.ext.commands import *
from discord.utils import get
import discord

# Other dependencies
from lib.helpers import url

COG_NAME = "Moderation"
MODS = ('**', 'Trial Mod')

def is_mod(ctx):
	for role in ctx.author.roles:
		if role.id in MODS:
			return True

def name_is_untypable(member):
	username_untypable = not all(ord(c) < 128 for c in member.name[0:4])
	nickname_untypable = not all(ord(c) < 128 for c in member.display_name[0:4])
	return username_untypable and nickname_untypable

class CogExt(Cog, name=COG_NAME):
	def __init__(self, bot):
		self.bot = bot

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

			# Code for moderating contest submissions
			if chnl.name == "contest-submissions":
				# If the message has text, there is an image, or more than 1 attachment then delete
				if cont != '' or len(msg.attachments) != 1 or msg.attachments[0].height is not None:
						await msg.delete()


	@Cog.listener()
	async def on_member_join(self, member):
		if name_is_untypable(member):
			await member.edit(nick="rule 11", reason="rule 11")

	@Cog.listener()
	async def on_member_update(self, before, after):
		if name_is_untypable(after):
			await after.edit(nick="rule 11", reason="rule 11")

	@command()
	@has_any_role(*MODS)
	async def is_untypable(self, ctx, member: discord.Member):
		await ctx.send(str(name_is_untypable(member)))

def setup(bot):
	bot.add_cog(CogExt(bot))
