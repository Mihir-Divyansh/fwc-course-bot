# The Discord Bot
The Bot runs in the following manner
## The Main File
`main.py` is the entry point for the bot application. It sets up the Discord bot, initializes cogs, and manages commands for setting active and inactive cogs, and reloading modules.

### Key Components

1. **Bot Setup:**
   - Configures intents for the bot.
   - Initializes the `commands.Bot` instance.

2. **Event Handlers:**
   - `on_ready()`: Logs a message when the bot is ready.

3. **Commands:**
   - `setactive(ctx: Context)`: Activates the `LoginCog` and `LinkCog` cogs.
   - `setinactive(ctx: Context)`: Deactivates the `LoginCog` and `LinkCog` cogs.
   - `reloadmodules(ctx: Context)`: Reloads various modules and updates global variables.

**Main Execution:**
> 1. `if __name__ == '__main__':`
   - Registers custom SQL adapters and converters.
   - Initializes global variables.
   - Runs the bot using the Discord API token from the configuration.

## Global Variables

`src/global_vars.py` manages global variables and initialization for the bot. It sets up configurations, connects to databases, and manages cogs for the bot.

### Attributes

1. **config** (`Config`): An instance of the `Config` class to manage configuration settings.
2. **databaseSQL** (`ManagerSQL`): An instance of the `ManagerSQL` class for SQL database management.
3. **mainTable** (`MainTable`): An instance of the `MainTable` class representing the main table in the database.
4. **roleQueueTables** (`Dict[str, RoleQueueTable]`): A dictionary mapping role names to `RoleQueueTable` instances.

### Methods

>  1. `reload_vars()`
Reloads global variables and configurations.

**Actions:**
- Reinitializes the `Config` instance.
- Reinitializes the `ManagerSQL` instance.
- Updates the `mainTable` and `roleQueueTables` global variables.

---

## Config

`Config` is a class that manages configuration settings for the bot by interacting with a JSON file containing secrets and configuration data. It provides methods to access configuration values and roles.

### Attributes

1. **secrets_file** (`str`): The path to the JSON file containing secrets and configuration data.
2. **secrets** (`serializers.SerializedJSON`): Serialized JSON object for accessing secrets.
3. **config_file** (`str`): The path to the configuration file retrieved from the secrets JSON file.
4. **__config** (`serializers.SerializedJSON`): Serialized JSON object for accessing configuration settings.
5. **discord_token** (`str`): The Discord API token retrieved from the secrets JSON file.

**Constructor:**
> `__init__(self, secretsJsonFile: str)`

Parameters:
- `secretsJsonFile`: The path to the JSON file containing secrets and configuration data.

### Methods

>  1. `get(self, key: str) -> dict | str | float | bool | None`
Retrieves a value from the configuration file based on the specified key.

Parameters:
- `key`: The key for the configuration setting.

Returns:
- The value associated with the key, which can be of type `dict`, `str`, `float`, `bool`, or `None`.

>  2. `getstr(self, key: str) -> str`
Retrieves a value from the configuration file as a string.

Parameters:
- `key`: The key for the configuration setting.

Returns:
- The value associated with the key as a string.

>  3. `getstrlower(self, key: str) -> str`
Retrieves a value from the configuration file as a lowercase string.

Parameters:
- `key`: The key for the configuration setting.

Returns:
- The value associated with the key as a lowercase string.

>  4. `get_role(self, roleID: int) -> str | None`
Retrieves the role name associated with the given role ID.

Parameters:
- `roleID`: The ID of the role.

Returns:
- The name of the role if found; otherwise, `None`.

>  5. `isRoleChannelDM(self, roleID: int) -> str | None`
Checks if the role ID corresponds to a role with DM channels.

Parameters:
- `roleID`: The ID of the role.

Returns:
- The DM channel information if found; otherwise, `None`.

>  6. `__getitem__(self, key)`
Retrieves a value from the configuration file based on the specified key.

Parameters:
- `key`: The key for the configuration setting.

Returns:
- The value associated with the key.

---


## LoginCog 

`LoginCog` is a class designed to handle registration, searching, and channel management for users in the server. The class verifies user details from an external registration database and manages Discord roles and channels accordingly. It logs every command execution and errors to dedicated log files.

### Attributes

1. **bot** (`discord.ext.commands.Bot`): The bot instance that this cog is attached to.
2. **guild** (`discord.Guild`): The Discord guild (server) where the cog is active.
3. **extdata** (`pd.DataFrame`): A Pandas DataFrame that loads the external registration database from a CSV file.
4. **category_count** (`dict`): A dictionary that stores the count of categories in the guild.
5. **channel_count** (`dict`): A dictionary that stores the count of channels within each category in the guild.

**Constructor:**
>`__init__(self, bot, guild)`

Parameters:

- `bot`: The Discord bot instance.
- `guild`: The Discord guild where the cog is active.



### Methods


>  1. `__get_from_ext_database(self, rollno: str)`
Retrieves user information from the external registration database.
>
Parameters:
- `rollno`: The roll number of the user to search for.

Returns: A tuple containing:
- `name` (str): The name of the user.
- `roleID` (int): The ID of the Discord role assigned to the user.
- `grpManagerRollNo` (str): The roll number of the user's group manager.

>  2. `register_logic(self, discordID: int, rollno: str) -> Tuple[str, MemberInfo]`
Handles the logic for registering a user

Checks if they are already registered, validating their roll number, and adding them to the database.

Parameters:
- `discordID`: The Discord ID of the user.
- `rollno`: The roll number of the user.

Returns: A tuple containing:
- `msg` (str): The result message of the registration attempt.
- `member` (MemberInfo): The member information if registration is successful, otherwise `None`.

>  3. `search_logic(self, fuzzy_name: str = '', rollno: str = '')`
Performs a fuzzy search for members based on their name or roll number.

Parameters:
- `fuzzy_name`: The fuzzy name search term.
- `rollno`: The roll number search term.

Returns: 
- `msg` (str): A message listing the found members or indicating no matches were found.

>  4. `on_member_join(self, member: discord.Member)`
Sends a welcome message to new members and instructs them on how to register.

Parameters:
- `member`: The new Discord member who joined the guild.



>  5. `__add_channel(self, base_category: str, member_a: MemberInfo, member_b: MemberInfo)`
Adds a new channel under a base category and assigns the necessary permissions to the concerned members.

Parameters:
- `base_category`: The base category name under which the channel will be created.
- `member_a`: The member information of the first member (usually the group manager).
- `member_b`: The member information of the second member.

>  6. `register(self, interaction: Interaction, rollno: str)`
Handles the `/register` command, allowing a user to register with their roll number.

Parameters:
- `interaction`: The interaction object containing the command context.
- `rollno`: The roll number provided by the user.
 

>  7. `registeruser(self, interaction: Interaction, user: discord.User, rollno: str)`
Handles the `/registeruser` command, allowing a maintainer to register a user with a specific roll number.

Parameters:
- `interaction`: The interaction object containing the command context.
- `user`: The Discord user to be registered.
- `rollno`: The roll number provided for the user.
 

## LinkCog 

`LinkCog` is a class that handles GitHub link evaluation, viewing, and approval in the server. It manages a queue of links to be reviewed, tracks their status, and interacts with Discord members to facilitate these processes.

### Attributes

1. **bot** (`discord.ext.commands.Bot`): The bot instance that this cog is attached to.
2. **github_regex** (`re.Pattern`): A compiled regular expression pattern to validate GitHub repository links.

**Constructor:**
> `__init__(self, bot) -> None`

Parameters:
- `bot`: The Discord bot instance.

### Methods

>  1. `eval_logic(self, discordID: int, link: str) -> Tuple[str, bool]`
Handles the logic for evaluating a GitHub link by adding it to a manager's queue for review.

Parameters:
- `discordID`: The Discord ID of the user submitting the link.
- `link`: The GitHub repository link to be evaluated.

Returns:
- `msg` (str): A message indicating the result of the evaluation attempt.
- `success` (bool): Whether the link was successfully added to the queue.

>  2. `view_logic(self, discordID: int) -> Tuple[str, MemberInfo]`
Handles the logic for viewing the current link under review by the manager.

Parameters:
- `discordID`: The Discord ID of the manager.

Returns:
- `msg` (str): A message detailing the current link under review, if any.
- `student` (MemberInfo): The member information of the student who submitted the link, if available.

>  3. `approve_logic(self, discordID: int) -> Tuple[str, bool]`
Handles the approval process for the current link being reviewed by a manager and escalates it to a higher level.

Parameters:
- `discordID`: The Discord ID of the manager approving the link.

Returns:
- `msg` (str): A message indicating the result of the approval attempt.
- `success` (bool): Whether the link was successfully approved and forwarded.

>  4. `view_status_logic(self, discordID: int) -> Tuple[str, bool]`
Returns the status of the links in the manager's queue, including pending, viewed, and currently viewing links.

Parameters:
- `discordID`: The Discord ID of the manager.

Returns:
- `msg` (str): A message summarizing the link status and viewing details.
- `success` (bool): Whether the status was successfully retrieved.

>  5. `eval(self, interaction: Interaction, link: str)`
Handles the `/eval` command for evaluating a GitHub link.

Parameters:
- `interaction`: The interaction object containing the command context.
- `link`: The GitHub repository link to be evaluated.

>  6. `view(self, interaction: Interaction)`
Handles the `/view` command to show the current link under review.

Parameters:
- `interaction`: The interaction object containing the command context.

>  7. `viewstats(self, interaction: Interaction)`
Handles the `/viewstats` command to show the status of the links in the manager's queue.

Parameters:
- `interaction`: The interaction object containing the command context.
