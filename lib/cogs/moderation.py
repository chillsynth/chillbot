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
		self.vars_loaded = False
		self.get_vars()


	def get_vars(self):
		if not self.vars_loaded:
			try:
				self.vc_chnl = get(self.bot.guild.voice_channels, name='voice chat')
				self.fb_chnl = get(self.bot.guild.voice_channels, name='feedback-stream')
				self.online_role = get(self.bot.guild.roles, name='Online')
				self.vars_loaded = True
			except AttributeError:
				return None


	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up(COG_NAME.lower())
		await self.bot.statchnl.send(f"`{COG_NAME}` cog loaded")

		self.get_vars()


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


	@command()
	@has_role('Feedback Hosts')
	async def fb(self, ctx, enable: bool):
		# Set permissions
		overwrite = PermissionOverwrite()
		overwrite.read_messages = enable
		overwrite.connect = enable
		await self.fb_chnl.set_permissions(self.online_role, overwrite=overwrite)

		await ctx.send("Feedback mode is now set to `"+str(enable)+"`")


	@command()
	@has_role('Feedback Hosts')
	async def fbmove(self, ctx):
		for member in self.fb_chnl.members:
				await member.move_to(self.vc_chnl)
		await ctx.send("Moved all members to <#543601182162157578>!")


def setup(bot):
	bot.add_cog(CogExt(bot))
