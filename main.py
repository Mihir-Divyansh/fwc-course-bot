# This python code runs the bot
# TODO: Make a #bot-only channel

import sys
import importlib

import aioconsole
import discord
import discord.ext
from discord.utils import get
from discord import app_commands, Interaction
from discord.ext.commands.context import Context

from src.sql_wrapper import *
from src.config import Config
import src.serializers as serializers

from src.global_vars import *
from src.register import *
from src.link_system import *

from loader import *

from addons.addons import *

@bot.event
async def on_ready():
    await bot.add_cog(LoginCog(bot))
    await bot.add_cog(LinkCog(bot))
    
    await bot.tree.sync()
    
    print(f'Logged in as {bot.user.name}')
    [print(f'{mainTable.getAllMembers()[i].name}: {mainTable.getAllMembers()[i].roleID}: {mainTable.getAllMembers()[i].rollno}') for i in range(len(mainTable.getAllMembers()))]
    print('Initialized Cogs, Login and Link Cogs are active now')

@bot.command('setactive')
@commands.has_role('Maintainer')
async def setactive(ctx : Context):
    
    await bot.add_cog(LoginCog(bot))
    await bot.add_cog(LinkCog(bot))
    await bot.tree.sync()
    print('Initialized Cogs, Login and Link Cogs are active now')

@bot.command('setinactive')
@commands.has_role('Maintainer')
async def setinactive(ctx : Context):
    await bot.remove_cog('LoginCog')
    await bot.remove_cog('LinkCog')
    await bot.tree.sync()
    
    print('Removed Cogs, Login and Link Cogs are inactive now')

@bot.command('reloadmodules')
@commands.has_role('Maintainer')
async def reloadmodules(ctx : Context):
    
    importlib.reload(sys.modules['src.serializers'])
    importlib.reload(sys.modules['src.logs'])
    importlib.reload(sys.modules['src.sql_wrapper'])
    importlib.reload(sys.modules['src.config'])
    importlib.reload(sys.modules['src.global_vars'])
    
    reload_vars()
    
    for keys, values in config['roles'].items():
        id = values['id']
        roleQueueTables[keys] = RoleQueueTable(id, databaseSQL)

    importlib.reload(sys.modules['src.register'])
    importlib.reload(sys.modules['src.link_system'])
    await bot.tree.sync()
    # print('Removed Cogs, Login and Link Cogs are inactive now')

# @bot.command('purgedb')
# @commands.has_role('Maintainer')
# async def purgeDB(ctx : Context):
#     mainTable.wipeDB('test/database.db')
#     return

if __name__ == '__main__':
    sql.register_adapter(serializers.SerializedJSON, serializers.adapt_sjson)
    sql.register_converter('SJSON', serializers.converter_sjson)

    for keys, values in config['roles'].items():
        id = values['id']
        roleQueueTables[id] = RoleQueueTable(id + 1, databaseSQL)

    bot.run(config.discord_token)


