from discord.ext.commands import *

COG_NAME = "Admin"

class CogExt(Cog, name=COG_NAME):
	def __init__(self, bot):
		self.bot = bot


	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up(COG_NAME.lower())
		await self.bot.statchnl.send(f"`{COG_NAME}` cog loaded")


def setup(bot):
	bot.add_cog(CogExt(bot))
