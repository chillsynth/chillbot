from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound
from discord.ext.commands.errors import *
from discord.ext.commands import command
from discord.ext.commands import is_owner
from discord import Game
import discord
from glob import glob
from asyncio import sleep
import logging

PREFIX = "cs."
OWNER_IDS = [265156354522611712]
COGS = [path.split("/")[2][:-3] for path in glob("lib/cogs/*.py")]

class Ready():
	def __init__(self):
		for cog in COGS:
			setattr(self, cog, False)

	def ready_up(self, cog):
		setattr(self, cog, True)

	def all_ready(self):
		return all([getattr(self, cog) for cog in COGS])

class Bot(BotBase):
	def __init__(self):
		self.PREFIX = PREFIX
		self.ready = False
		self.cogs_ready = Ready()
		super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS, intents=discord.Intents().all())

	def setup(self):
		for cog in COGS:
			self.load_extension(f"lib.cogs.{cog}")
			print(f'- "{cog.capitalize()}" cog loaded!')

	def run(self, version):
		self.VERSION = version

		print("Loading cogs...")
		self.setup()

		with open("./lib/bot/token.0", 'r', encoding="utf-8") as tf:
			self.TOKEN = tf.read().strip()

		print("Running bot...")
		super().run(self.TOKEN, reconnect=True)	

	async def on_ready(self):
		if not self.ready:

			# Set important attributes
			self.statchnl = self.get_channel(517654463280840704)
			self.guild = self.get_guild(488405912659427358)

			while not self.cogs_ready.all_ready():
				await sleep(0.5)

			print(f'\nLogged in as {self.user.name} (ID:{self.user.id})')
			print('--------')
			print('Created by npgy#2000\n')
			await self.change_presence(activity=Game(name='Corporate Shillwave'))

			self.ready = True
			print("Bot Ready.")

			await self.statchnl.send("Now online!")
		else:
			print("Bot reconnected.")

	async def on_message(self, message):
		if not message.author.bot:
			await self.process_commands(message)

	async def on_connect(self):
		print("Bot connected.")

	async def on_disconnect(self):
		print("Bot disconnected.")

	async def on_error(self, err, *args, **kwargs):
		if err == "on_command_error":
			await args[0].send("Something went wrong.")

		raise

	async def on_command_error(self, ctx, exc):
		if isinstance(exc, CommandNotFound):
			pass
		elif isinstance(exc, CheckFailure):
			await ctx.send("Sorry, you don't have permission to run this command.")
		elif isinstance(exc, MissingRole):
			await ctx.send("Sorry, you don't have permission to run this command.")
		elif hasattr(exc, "original"):
			raise exc.original
		else:
			raise exc


bot = Bot()

@bot.command()
@is_owner()
async def stop(ctx):
	await ctx.send("Bot has stopped completely.")
	await bot.close()

@bot.command()
async def load(ctx, extension):
	bot.load_extension(f'lib.cogs.{extension}')
	cog_msg = f'`{extension.capitalize()}` cog loaded!'
	await ctx.send(cog_msg)
	print(cog_msg)

@bot.command()
async def unload(ctx, extension):
	bot.unload_extension(f'lib.cogs.{extension}')
	cog_msg = f'`{extension.capitalize()}` cog unloaded!'
	await ctx.send(cog_msg)
	print(cog_msg)

@bot.command()
async def reload(ctx, extension):
	bot.unload_extension(f'lib.cogs.{extension}')
	bot.load_extension(f'lib.cogs.{extension}')
	cog_msg = f'`{extension.capitalize()}` cog reloaded!'
	await ctx.send(cog_msg)
	print(cog_msg)
