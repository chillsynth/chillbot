# Import discord dependencies
from discord import PermissionOverwrite
from discord.ext.commands import *
from discord.utils import get

# Other dependencies
from lib.helpers import url

COG_NAME = "Moderation"
MODS = ('Moderator', 'Lowkey Mod', 'Crew')

def is_mod(ctx):
	for role in ctx.author.roles:
		if role.id in MODS:
			return True

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


	@command()
	@has_any_role(*MODS)
	async def secret(self, ctx):
		await ctx.send("poopy butthole!")


def setup(bot):
	bot.add_cog(CogExt(bot))
