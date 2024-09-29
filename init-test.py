# This python file is to test the register and links modules

from src.sql_wrapper import *
from src.config import Config
import src.serializers as serializers

from src.register import *
from src.link_system import *

sql.register_adapter(serializers.SerializedJSON, serializers.adapt_sjson)
sql.register_converter('SJSON', serializers.converter_sjson)

loginCog = LoginCog(None)

for keys, values in config['roles'].items():
    id = values['id']
    roleQueueTables[id] = RoleQueueTable(id + 1, databaseSQL)

# Test register_logic
print(loginCog.register_logic(705631226475839518, 'fwc-00000')) # Wrong Roll no format
print(loginCog.register_logic(691702106284883998, 'fwc-99989')) # Successfull registration
print(loginCog.register_logic(1242104002737340478, 'fwc-99988')) # Duplicate registration
