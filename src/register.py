import discord
import discord.ext
from discord.utils import get
from discord import app_commands, Interaction
from discord.ext.commands.context import Context
from discord.ext.commands import Cog

import re
import pandas as pd
from src.global_vars import *

from typing import Tuple

# Start writing register module here
# Print detailed erros and warnings to logs.log
# Log every command executed to logs.cmd

# example function
# @bot.tree.command(name='helloworld')
# async def print_helloworld(interaction : Interaction):
#     logs.cmd.info(f'Member({interaction.user.id}) used /helloworld')

#     # This is a try-catch block[Search online if you don't know what this does]
#     try:
#         # Use the ephemeral toggle when you want only the user(who ran the command) to see
#         # the response
#         await interaction.response.send_message('Hello, World', ephemeral=True)
#     except Exception as e:
#         # Some Error occurred
#         logs.log.error(f'Exception occured in /helloworld: {e}')

# This cog deals with register
class LoginCog(Cog):
    def __init__(self, bot : commands.Bot):
        self.extdata = pd.read_csv(config['registrations-database'])
        self.bot = bot
        if not bot:
            return
        self.guild : discord.Guild = bot.guilds[0]
        self.category_count = {}
        self.channel_count = {}
        for category in self.guild.categories:
            base_name = category.name[:-2]
            if base_name not in self.category_count:
                self.category_count[base_name] = 0
            self.category_count[base_name] += 1
            self.channel_count[category.name] = len(category.text_channels)
            
    def __get_from_ext_database(self, rollno : str):
        print(self.extdata)
        try:
            print([self.extdata['roll-no'] == rollno.lower()])
            name = self.extdata['name'][self.extdata['roll-no'] == rollno.lower()].values[0].strip()
            print(name)
            role_name = self.extdata['discord-role-name'][self.extdata['roll-no'] == rollno.lower()].values[0].strip()
            grpManagerRollNo = self.extdata['group-manager-rollno'][self.extdata['roll-no'] == rollno.lower()].values[0].strip().lower()
            print(grpManagerRollNo)
        except Exception as e:
            logs.log.error('Exception while searching rollno {rollno}: %s', e)
            return ('', -1, '')

        return (name, config[f'roles/{role_name}/id'], grpManagerRollNo)

    def register_logic(self, discordID : int , rollno : str) -> Tuple[str, MemberInfo]:
        rollno = rollno.lower().strip()
        print(rollno)
        
        if mainTable.isMember(rollno=rollno):
            clashing_member = mainTable.getMember(rollno=rollno)
            if clashing_member.discordID != discordID:
                msg  =  'Registration Clash:\n'
                msg += f'\tIncoming:[{discordID=}, {rollno=}]\n'
                msg += f'\tPrevious:[{clashing_member.discordID=}, {clashing_member.rollno=}]\n'
                logs.log.error(msg)
                return f"Roll number {rollno} is already registered by {clashing_member.name}.\n", None
            else:
                return f"You are already registered.\n", None
        if mainTable.isMember(discordID=discordID):
            logs.log.error(f"Member({discordID}) tried registering again with roll no ({rollno})")
            return f"Member {discordID} is already registered.", None

        if len(rollno) == 0:
            logs.log.error(f"Registering member({discordID}). Roll number or GitHub ID not given")
            msg = 'Syntax: /register roll-no\n'
            msg += 'Example Usage: /register fwc-00000\n'
            msg += 'Use the above format. You did not enter the information required.'
            return msg, None
        
        if rollno == 'rollno':
            logs.log.error(f'Member({discordID}) registeration failed. Invalid roll-no/github-id')
            msg = 'Invalid roll no\n'
            msg += 'Syntax: /register roll-no\n'
            msg += 'Example Usage: /register fwc-00000\n'
            msg+= 'Use the above format. You did not enter the information required.'
            return msg, None

        if not re.findall(config['rollno/regex'], rollno):
            roll_no_regex = config['rollno/regex']
            roll_no_syntax = config['rollno/syntax']
            logs.log.error(f'Roll-No({rollno=}) did not match regex: {roll_no_regex}')
            return f"Please enter roll number in the format {roll_no_syntax} and run the command again.", None

        name, roleID, gManager = self.__get_from_ext_database(rollno)
        print(name, roleID, gManager)
        if not name:
            return f'The roll-no {rollno} is not in the course. Check if the entered roll number is correct and try again. {roleID=}', None

        try:
            newMember = mainTable.addMember(discordID=discordID, name=name, rollno=rollno, roleID=roleID, groupManager=gManager)
            logs.log.info(f'Member({discordID}) registered successfully')
            return f"Registration Successful", newMember
        except Exception as e:
            logs.log.error(f'Member({discordID}) registration failed. Fatal Exception occurred: %s', e, stack_info=True, exc_info=True)
            return "There was an unknown error in registering. This incident has been reported to the maintainers. Try registering again in a few hours", None

    # fuzzy search
    def search_logic(self, fuzzy_name : str = '', rollno : str = ''):
        members = mainTable.getMembersFuzzy(name=fuzzy_name, rollno=rollno)
        
        if not members:
            return 'Did not find any member matching the given input!'
        
        msg = 'Found Member(s):\n'
        
        for member in members:
            if fuzzy_name:
                msg += f'{member.name} {member.discordID}\n'
            elif rollno:
                msg += f'{member.rollno} {member.name} {member.discordID}\n'
        
        return msg.strip()

    @commands.Cog.listener()
    async def on_member_join(self, member : discord.Member):
        member.send(f'Welcome, {member.name}.\nUse /register with your roll number and github user name to use discord channels.')

    # adds a channel to a "base" category, and adds the concerned members
    # assuming both registered
    async def __add_channel(self, base_category : str, member_a : MemberInfo, member_b : MemberInfo):
        if base_category not in self.category_count:
            self.category_count[base_category] = 0
            self.channel_count[base_category + '-0'] = 0
        
        last_id : int = self.category_count[base_category]
        category_name = f'{base_category}-{last_id}'
        
        category = discord.utils.get(self.guild.categories, name=category_name)
        if category is None:
            try:
                category = await self.guild.create_category(category_name)
                print(f"Created category: {category.name}")
            except Exception as e:
                print(f"Failed to create category '{category_name}': {e}")
                return
        
        if self.channel_count[category_name] >= 50:
            last_id += 1
            
            category = get(self.guild.categories, name=category_name)
            if category is None:
                try:
                    category = await self.guild.create_category(category_name)
                    self.category_count[base_category] += 1
                    self.channel_count[category_name] = 0
                    print(f"Created category: {category.name}")
                except Exception as e:
                    print(f"Failed to create category '{category_name}': {e}")
                    return
        
        lusername = member_b.name.lower().replace(' ', '-')
        channel_name = f"{lusername}-{member_b.rollno}-{member_a.roleID}"
        # Checking if the channel already exists
        existing_channel = get(category.channels, name=channel_name)
        if existing_channel:
            print(f"Channel '{channel_name}' already exists in category '{category.name}'")
            return
        
        member = get(self.guild.members, id=member_b.discordID)
        manager = get(self.guild.members, id=member_a.discordID)

        #Mention Overwrites
        overwrites = {
            self.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            manager: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        try:
            channel = await self.guild.create_text_channel(channel_name, overwrites=overwrites, category=category)
            print(f"Created text channel: {channel.name} for {member.name} in category {category.name}")
        except Exception as e:
            print(f"Failed to create text channel for {member.name}: {e}")

    @app_commands.command(name='register', description='Register with your roll number')
    async def register(self, interaction: Interaction, rollno: str):
        # print(interaction.user.roles())
        print(rollno)
        logs.cmd.info(f'{interaction.user.name}(id:{interaction.user.id}) used /register({rollno=})')

        msg, member = self.register_logic(interaction.user.id, rollno=rollno)

        if not member:
            try:
                await interaction.response.send_message(msg, ephemeral=True)
            except Exception as e:
                logs.log.error('Error: Fatal Exception occurred in register: %s', e)
            return
        # print(member.groupManagerRollNo)

        # Assign role
        member_rolename = config.get_role(member.roleID)
        # print(member_rolename)
        role = get(interaction.guild.roles, name=member_rolename)
        if role:
            await interaction.user.add_roles(role)
        else:
            logs.log.error(f"Role '{member_rolename}' not found in the guild.")
        
        await interaction.response.defer(thinking=True)
        # print(config[f'roles/{member_rolename}/dm-channels'])
        # Handle DM channels
        if config[f'roles/{member_rolename}/dm-channels']:
            manager = mainTable.getMember(rollno=member.groupManagerRollNo)
            # if not manager:
            #     logs.log.error(f"Manager for member {member.name} not found.")
            old_rollno = ''
            while old_rollno != manager.rollno:
                manager_rolename = config.get_role(manager.roleID)
                if not config[f'roles/{manager_rolename}/dm-channels']:
                    old_rollno = manager.rollno
                    manager = mainTable.getMember(rollno=manager.groupManagerRollNo)
                    continue
                manager_cat_name = config[f'roles/{manager_rolename}/cat-name']
                member_cat_name = config[f'roles/{member_rolename}/cat-name']
                category_basename = f'{manager_cat_name.strip().lower().replace(" ", "-")}-{member_cat_name.strip().lower().replace(" ", "-")}'
                await self.__add_channel(category_basename, manager, member)

                old_rollno = manager.rollno
                manager = mainTable.getMember(rollno=manager.groupManagerRollNo)

        try:
            await interaction.followup.send(msg)
        except Exception as e:
            logs.log.error('Error: Fatal Exception occurred in register: %s', e)


    @app_commands.command(name='registeruser', description="Allows a maintainer to register the user.")
# @app_commands.has_role('Maintainer')
    async def registeruser(self, interaction: Interaction, user: discord.User, rollno: str):
        # Check for maintainer role
        maintainer_role = discord.utils.get(interaction.guild.roles, name='Maintainer')
        if maintainer_role not in interaction.user.roles:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        # Log the interaction
        logs.cmd.info(f'{interaction.user.name} used /registeruser on {user.name}({user.id}) with {rollno=})')
        print(rollno)
        
        # Your custom registration logic
        msg, member_data = self.register_logic(user.id, rollno=rollno)
        # print(member_data)
        # print(msg)
        
        if not member_data:
            try:
                await interaction.response.send_message(msg, ephemeral=True)
            except Exception as e:
                logs.log.error(f'Error: Fatal Exception occurred in register: {e}')
            return

        print(member_data.name)
        
        # Fetch the role to assign
        member_rolename = config.get_role(member_data.roleID)
        role = discord.utils.get(interaction.guild.roles, name=member_rolename)
        
        # Roles can only be assigned to member objects
        # which are users in context of a guild.
        member = interaction.guild.get_member(user.id) 
        # print(member.name)
        if member is None:
            await interaction.response.send_message("Could not find the member in the guild.", ephemeral=True)
            return
        
        print(role.name)

        await member.add_roles(role)
        
        if role in member.roles:
            print(f"Successfully given role: {role.name}")
        else:
            print(f"Failed to assign role to user: {member.display_name}")
        
        try:
            await interaction.response.send_message(msg, ephemeral=True)
        except Exception as e:
            logs.log.error(f'Error: Fatal Exception occurred in register: {e}')





