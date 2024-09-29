# This python code loads all the discord modules

import discord
from discord.ext import commands

# set up discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix = '/', intents = intents)


