# FWC Course Bot - Developer Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Setup Instructions](#setup-instructions)
4. [Project Structure](#project-structure)
5. [Configuration](#configuration)
6. [Database](#database)
7. [Bot Commands](#bot-commands)
8. [Add-ons](#add-ons)
9. [Logging](#logging)
10. [Testing and Debugging](#testing-and-debugging)
11. [Contributing](#contributing)

---
## Overview

The **FWC Course Bot** is a Discord bot designed to manage student interactions for a course. It automates tasks such as registration, project submissions, and role management. The bot is extensible via add-ons and integrates with external services like Google Sheets for data synchronization. SQLite is used for database management, and the front end is powered by [discord.py](https://github.com/Rapptz/discord.py).

This documentation provides instructions for setting up, configuring, and extending the bot.

---

## System Requirements

- **Python** 3.10+
- **pip** (Python package manager)
- **SQLite** database (configurable)
- **Discord bot token** (setup instructions [here](https://arjancodes.com/blog/how-to-build-a-simple-discord-bot/))
- **Google Sheets API credentials** (if using Google Sheets add-on)

---

## Setup Instructions

To set up the bot locally for development:

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd fwc-course-bot
   ```

2. **Install Dependencies**:
   Create a virtual environment and install the required Python packages:
   ```bash
   pip install -r reqs.txt
   ```

3. **Configure the Bot**:
   Update the configuration files in the `configs/` directory. For example:
   - `base-config.json`: General configuration.
   - `config-prod.json`: Production-specific settings.
   - `gsheet-config.json`: Google Sheets configuration.

4. **Initialize the Database**:
   Run the following script to set up the database schema:
   ```bash
   python initDB.py
   ```

5. **Run the Bot**:
   Start the bot by executing:
   ```bash
   python main.py
   ```

---

## Project Structure

The project is organized as follows:

```bash
fwc-course-bot/
├── addons/                # Extendable bot features
│   ├── hello_world.py
│   ├── gsheets_addon.py
│   └── google-sheets/
│       └── logic.py
├── configs/               # Configuration files
│   ├── config-prod.json
│   ├── gsheet-config.json
│   └── base-config.json
├── docs/                  # Documentation
│   ├── usage.md
│   ├── SQL.md
│   └── Discord.md
├── ext/                   # External data
│   └── registered.csv
├── logs/                  # Log files
├── src/                   # Core bot functionality
│   ├── config.py
│   ├── link_system.py
│   ├── sql_wrapper.py
│   ├── global_vars.py
│   ├── serializers.py
│   └── console/
│       └── cmain.py
├── initDB.py              # Script to initialize the database
├── loader.py              # Loader for the bot
├── main.py                # Main entry point for the bot
├── reqs.txt               # Dependencies file
└── README.md              # Project overview and documentation
```

---

## Configuration

Configuration files are stored in the `configs/` directory. The main configuration file is `base-config.json`, which contains general settings. The bot also supports environment-specific configurations like `config-prod.json` for production and `config-test.json` for testing.

**Sample `base-config.json`**:
```json
{
    "config" : "configs/config-prod.json",
    "sql-database" : "path_to_database",
    "discord-api-token" : "your_token_here"
}
```

The `config-prod.json` file contains settings like:

- Role hierarchy
- Path to the SQL database
- Add-on information

### Role Hierarchy

The bot organizes roles in a hierarchical structure, where the topmost role is `GVV`. Each role has attributes like `name`, `category name`, `ID`, and `DM channels`. Roles can also have child roles under their control.

**Sample Role Hierarchy**:
```json
{
    "roles": {
        "GVV Sharma": {
            "name": "GVV Sharma",
            "cat-name": "gvv",
            "id": 0,
            "dm-channels": true,
            "child-roles": ["PM", "TA"]
        },
        "TA": {
            "name": "TA",
            "cat-name": "ta",
            "id": 1,
            "dm-channels": true,
            "child-roles": ["Module - Student"]
        }
    }
}
```

---

### The SQLight side of things
For details about SQL Manager, look at [The Documentation](/docs/SQL.md)


The bot uses SQLite to store persistent data. SQL operations are handled by the `src/sql_wrapper.py` module. To initialize the database, run the `initDB.py` script, which sets up the required schema.

For more details on database management, refer to the [SQL Documentation](/docs/SQL.md).

---

## Bot Commands

The bot provides various commands for user and role management. Commands are defined in `main.py`, and additional functionality can be added via the add-ons in the `addons/` directory.

Command examples:
- `/register`: Registers a user.
- `/eval`: Sends a submission for evaluation.
- `/view`: Views a user's submission.
- `/approve` : Sends the submission up to the higher role.

Detailed information about the commands can be found in the [Discord Documentation](/docs/Discord.md) and [Usage Documentation](/docs/usage.md).

---

## Add-ons (Experimental)

The bot is designed to be extensible via add-ons located in the `addons/` directory. Add-ons allow developers to add new features to the bot without modifying the core code.

**Example Add-ons**:
- **`hello_world.py`**: A simple example of an add-on.
- **`gsheets_addon.py`**: Integrates the bot with Google Sheets for data synchronization.

To create a new add-on, use `hello_world.py` as a template and place the new add-on in the `addons/` folder.

---

## Logging

Logs are stored in the `logs/` directory. The logging behavior, such as log levels and formats, can be configured in `base-config.json`.

By default, the bot logs:
- Errors
- Warnings
- Important events (e.g., user commands)

---

## Testing and Debugging

To test the bot's functionality, there are test scripts located in the root directory:
- `test.py`: General test script for bot commands.
- `test-sql.py`: Tests the SQL wrapper and database interactions.

For debugging, you can use:
- **`print()`** statements in the code.
- Check log files in the `logs/` directory for detailed error messages.

---

## Contributing

If you're contributing to the FWC Course Bot, make sure to follow these guidelines:

1. Stick to the existing coding conventions and style.
2. Write clear and descriptive commit messages.
3. Add comments and documentation for new features.
4. Test your changes thoroughly before pushing them.

