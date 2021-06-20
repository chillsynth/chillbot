# Import discord dependencies
from discord import PermissionOverwrite
from discord.ext.commands import *
from discord.utils import get
import random
import discord

# Other dependencies
from lib.helpers import url

COG_NAME = "Events"

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
				self.event_strm = self.bot.get_channel(691009984418414602)
				self.event_chat = self.bot.get_channel(807035168404930572)
				self.vc_chnl = self.bot.get_channel(543600804180000788)
				self.online_role = get(self.bot.guild.roles, name='Online')
				self.vars_loaded = True
			except AttributeError:
				return None


	@command(aliases=['em'])
	@has_role('Event Host')
	async def eventmode(self, ctx, enable: bool):
		# Set permissions
		await self.event_strm.set_permissions(self.online_role, read_messages=enable, connect=enable)
		await self.event_chat.set_permissions(self.online_role, send_messages=enable)

		await ctx.send("Event mode is now set to `"+str(enable)+"`")

	@command()
	@has_role('Event Host')
	async def eventmove(self, ctx):
		for member in self.event_strm.members:
				await member.move_to(self.vc_chnl)
		await ctx.send("Moved all members to <#543600804180000788>!")

	@command()
	@has_role('Event Host')
	async def eventsize(self, ctx):
	    await ctx.send("There are `"+str(len(self.event_strm.members))+"` people in the event stream!")

	@command()
	@has_role('**')
	async def randreact(self, ctx, msg: discord.Message):
		users = await msg.reactions[0].users().flatten()
		winner = random.choice(users)
		await ctx.send(f'{winner.mention} is the lucky winner!')


def setup(bot):
	bot.add_cog(CogExt(bot))
