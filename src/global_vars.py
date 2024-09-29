import discord
from discord.ext import commands

from typing import List, Dict

from src.config import Config
from src.sql_wrapper import *
import src.logs as logs

global config
global roleQueueTables
global mainTable
global databaseSQL

config : Config = Config('configs/base-config.json')
databaseSQL : ManagerSQL = ManagerSQL(config['sql-database'])
mainTable : MainTable = MainTable(0, databaseSQL)
roleQueueTables : Dict[int, RoleQueueTable] = {}

def reload_vars():
    config : Config = Config('configs/base-config.json')
    databaseSQL : ManagerSQL = ManagerSQL(config['sql-database'])
    mainTable : MainTable = MainTable(0, databaseSQL)
    roleQueueTables : Dict[int, RoleQueueTable] = {}

