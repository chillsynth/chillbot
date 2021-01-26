from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.utils import get
from asyncio import sleep

COG_NAME = "Greetings"

class CogExt(Cog, name=COG_NAME):
	def __init__(self, bot):
		self.bot = bot
		self.vars_loaded = False
		self.get_vars()


	def get_vars(self):
		if not self.vars_loaded:
			try:
				self.online_role = get(self.bot.guild.roles, name='Online')
				self.lounge_chnl = get(self.bot.guild.channels, name="chill-lounge")
				self.vars_loaded = True
			except AttributeError:
				return None


	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up(COG_NAME.lower())
		await self.bot.statchnl.send(f"`{COG_NAME}` cog loaded")

		self.get_vars()


	# On member update event
	@Cog.listener()
	async def on_member_update(self, before, after):
		if not before.bot:
			if before.pending == True and after.pending == False:
				if self.online_role not in before.roles:
					await sleep(0.2)
					await after.add_roles(after.guild.get_role(631849829026496543), reason="User verification")
					await self.lounge_chnl.send("Hello "+before.mention+" and welcome to ChillSynth!\n"+
					"Please remember to get your roles in <#583960398961573919> (scroll to the top for Music Producer!)\n"+
					"And as always, **GIVE** <#488440534449258527> before you **ASK** for it!")


def setup(bot):
	bot.add_cog(CogExt(bot))
