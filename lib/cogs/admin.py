from discord.ext.commands import *
import discord

COG_NAME = "Admin"

class CogExt(Cog, name=COG_NAME):
	def __init__(self, bot):
		self.bot = bot

	## EVENTS

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up(COG_NAME.lower())
		await self.bot.statchnl.send(f"`{COG_NAME}` cog loaded")


	## COMMANDS

	@command()
	@has_role('**')
	async def invite(self, ctx, channel: discord.TextChannel, age, uses):
		inv = await channel.create_invite(max_age=age, max_uses=uses)
		await ctx.send(f"Successfully created invite `{str(inv)}` for channel <#{channel.id}>")

def setup(bot):
	bot.add_cog(CogExt(bot))
