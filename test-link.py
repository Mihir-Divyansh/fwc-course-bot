# This python file is to test the register and links modules

from src.sql_wrapper import *
from src.config import Config
import src.serializers as serializers

from src.register import *
from src.link_system import *

sql.register_adapter(serializers.SerializedJSON, serializers.adapt_sjson)
sql.register_converter('SJSON', serializers.converter_sjson)

loginCog = LoginCog('something', 'tmp')
linkCog = LinkCog('something', 'tmp')

for keys, values in config['roles'].items():
    id = values['id']
    roleQueueTables[id] = RoleQueueTable(id + 1, databaseSQL)

# Test register_logic
print(loginCog.register_logic(42, 'fwc-00')) # Wrong Roll no format
print(loginCog.register_logic(42, 'fwc-00001')) # Successfull registration
print(loginCog.register_logic(42, 'fwc-00001')) # Duplicate registration
print(loginCog.register_logic(42, 'fwc-00002')) # Malicious registration
print(loginCog.register_logic(42, 'fwc-00010')) # Malicious registration(not a rollno)
print(loginCog.register_logic(69, 'fwc-00001')) # Clashing registration
print(loginCog.register_logic(69, 'fwc-00010')) # Malicious registration(not a rollno)
print(loginCog.register_logic(69, 'fwc-00002')) # Successfull registration
print(loginCog.register_logic(73, 'fwc-00000')) # Successfull registration

print(loginCog.register_logic(32104832984, 'fwc-99988')) # Successfull registration

# Test eval link logic
print(linkCog.eval_logic(420, 'https://github.com/Soham-More/Course-Bot/tree/main')) # unregistered discord id
print(linkCog.eval_logic(69, 'https://google.com/Soham-More/Course-Bot/tree/main')) # wrong link
print(linkCog.eval_logic(69, 'https://github.com/Soham-More/Course-Bot/tree/main')) # Queue Succesfully
print(linkCog.eval_logic(69, 'https://github.com/Soham-More/Course-Bot/tree/main')) # Duplicate Link
print(linkCog.eval_logic(69, 'https://github.com/Soham-More/Course-Bot/tree/master')) # Queue Succesfully

print(linkCog.view_logic(420)) # unregistered discord id
print(linkCog.view_logic(42)) # successfull view

print(linkCog.approve_logic(420)) # unregistered discord id
print(linkCog.approve_logic(42)) # approve

print(linkCog.view_logic(42)) # successfull view
print(linkCog.view_logic(42)) # finished viewing all links

print(linkCog.view_logic(73)) # successfull view of approved link
print(linkCog.view_logic(73)) # finished viewing all links


print(loginCog.search_logic(fuzzy_name='name'))
