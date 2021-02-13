from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.utils import get

COG_NAME = "Fun"

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
				self.fb_chnl = get(self.bot.guild.voice_channels, name='feedback-stream')
				self.vars_loaded = True
			except AttributeError:
				return None


	@command()
	async def fb_size(self, ctx):
	    await ctx.send("There are `"+str(len(self.fb_chnl.members))+"` people in the feedback stream!")

def setup(bot):
	bot.add_cog(CogExt(bot))
