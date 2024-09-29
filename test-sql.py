# This python file is to test the SQL related modules

from src.sql_wrapper import *
from src.config import Config
import src.serializers as serializers

config : Config = Config('configs/base-config.json')

msql : ManagerSQL = ManagerSQL(config['sql-database'])
mainTable = MainTable(0, msql)

mainTable.addMember(discordID=69, name='Soham More', rollno='fwc897', roleID=config['roles/top_role/id'])

print()
