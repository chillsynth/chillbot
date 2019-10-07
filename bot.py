# These are the dependencies. The bot depends on these to function, hence the name. Please do not change these
import discord
import json
import os
import asyncio
from platforms import *
from discord.ext.commands import Bot
from discord.ext import commands
from discord.utils import get

# Important globals
me = 265156354522611712
mod_roles = ["Moderator","Crew"]

# Prefix functions
prfx = 'cs.'

# Here you can modify the bot's prefix and description and whether it sends help in direct messages or not.
TOKEN = open("token.txt","r").read().strip()
bot = Bot(description="ChillBot by npgy#2000", command_prefix=prfx, pm_help = True)

# Bot on ready event
@bot.event
async def on_ready():
    # general boot up stuff
    print(f'Logged in as {bot.user.name} (ID:{bot.user.id}) | Connected to {len(set(bot.get_all_members()))} users')
    print('--------')
    print('Created by npgy#2000')
    await bot.change_presence(activity=discord.Game(name='Corporate Shillwave'))

# On message event
@bot.event
async def on_message(msg):

    #Define useful shortcuts
    cont = msg.content
    chnl = msg.channel
    author = msg.author
    guild = msg.guild

    if author.bot:
        return

    # Code for moderating #new-releases
    if chnl.name == "new-releases":
        if not Platforms.one_pltfrm_in_str(cont):
            await msg.delete()

    # Allow commands to be processed from the message if nothing was run here
    # await bot.process_commands(msg)

bot.run(TOKEN)