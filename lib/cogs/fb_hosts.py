# Import discord dependencies
from discord import PermissionOverwrite
from discord.ext.commands import *
from discord.utils import get

# Other dependencies
from lib.helpers import url

COG_NAME = "Feedback Hosts"

class CogExt(Cog, name=COG_NAME):
	def __init__(self, bot):
		self.bot = bot
		self.vars_loaded = False
		self.get_vars()

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up(COG_NAME.lower())
		await self.bot.statchnl.send(f"`{COG_NAME}` cog loaded")

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


	@command()
	@has_role('Feedback Hosts')
	async def fb(self, ctx, enable: bool):
		#Get Groovy member object
		groovy = self.bot.guild.get_member(234395307759108106)
		radio_control = get(self.bot.guild.text_channels, name='radio-control')
		radio_vc = get(self.bot.guild.voice_channels, name='radio')

		# Set permissions
		await self.fb_chnl.set_permissions(self.online_role, read_messages=enable, connect=enable)
		await self.vc_chnl.set_permissions(groovy, view_channel=not enable, connect=not enable)
		await radio_control.set_permissions(groovy, read_messages=not enable)
		await radio_vc.set_permissions(groovy, view_channel=not enable, speak=not enable)

		await ctx.send("Feedback mode is now set to `"+str(enable)+"`")


	@command()
	@has_role('Feedback Hosts')
	async def fbmove(self, ctx):
		for member in self.fb_chnl.members:
				await member.move_to(self.vc_chnl)
		await ctx.send("Moved all members to <#543601182162157578>!")


def setup(bot):
	bot.add_cog(CogExt(bot))
