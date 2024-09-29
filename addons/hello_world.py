
import discord
import discord.ext
from discord.utils import get
from discord import app_commands, Interaction
from discord.ext.commands.context import Context

from loader import *

@bot.command('addons_hw')
async def addon_hw(ctx : Context):
    print('Hello, World')
