# This file initializes/updates the SQL DB
# It is not related to discord
# and should need root previleges
# to execute
# This generates a json file for sql_manager
# That way sql_manager can parameterize the inputs to itself

import sqlite3 as sql

import json
import re

from src.config import Config
import src.serializers as serializers

config : Config = Config('configs/base-config.json')
sql_db = sql.connect(config['sql-database'], detect_types=sql.PARSE_DECLTYPES)
con = sql_db.cursor()

def register_serializers():
    sql.register_adapter(serializers.SerializedJSON, serializers.adapt_sjson)
    sql.register_converter("JSON", serializers.converter_sjson)

def run(cmd, data=()):
    try:
        con.execute(cmd, data)
        return con.fetchall()
    except Exception as e:
        raise Exception(f'Error executing/fetching SQL: {cmd}, {data}\n\t{e}')

def write(cmd, data=()):
    try:
        con.execute(cmd, data)
        result = con.fetchall()
        sql_db.commit()
        return result
    except Exception as e:
        raise Exception(f'Error executing/fetching SQL: {cmd}, {data}\n\t{e}')

def isTableExisting(tableIndex : int):
    return len(run(f"SELECT name FROM sqlite_master WHERE type='table' AND name='table_{tableIndex}';")) > 0

def createTable(tableIndex : int, isMainTable : bool = False):
    columns = []

    if isMainTable:
        columns = config['mainTableColumns']
    else:
        columns = config['roleQueueColumns']

    columns = ','.join(columns)

    run(f"CREATE TABLE table_{tableIndex}({columns});")

register_serializers()

# check if the main table exists
# if it does not, make it
if not isTableExisting(0):
    createTable(0, isMainTable=True)

id_list = []

for key, value in config['roles'].items():
    # print(config['roles'])
    id = value['id']
    # print(id)
    if id in id_list:
        raise Exception(f'Error: ID({id}) reassigned to role {key}')
    if not isTableExisting(id + 1):
        createTable(id + 1)

con.close()
sql_db.close()