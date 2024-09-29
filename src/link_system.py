import discord
import discord.ext
from discord.utils import get
from discord import app_commands, Interaction
from discord.ext.commands.context import Context
from discord.ext.commands import Cog

import re
import time
import datetime
from src.global_vars import *

def pretty_format_deltatime(timeAfter, timeBefore):
    deltaseconds = timeAfter - timeBefore
        
    days = int(deltaseconds) // ( 3600 * 24 )
    hours = int(deltaseconds) // ( 3600 )
    minutes = int(deltaseconds) // ( 60 )
    seconds = int(deltaseconds)
    
    show_time = ''

    if days > 1:
        show_time = '' + str(days) + ' day ago'
    elif days > 0:
        show_time = '' + str(days) + ' days ago'
    elif hours > 1:
        show_time = '' + str(hours) + ' hour ago'
    elif hours > 0:
        show_time = '' + str(hours) + ' hours ago'
    elif minutes > 1:
        show_time = '' + str(minutes) + ' minute ago'
    elif minutes > 0:
        show_time = '' + str(minutes) + ' minutes ago'
    elif seconds > 1:
        show_time = '' + str(seconds) + ' second ago'
    elif seconds > 0:
        show_time = '' + str(seconds) + ' seconds ago'
    else:
        show_time = 'just now'

    return show_time

def getMemberQueue(member : MemberInfo):
    print(member.roleID)
    return MemberQueue(member.rollno, roleQueueTables[member.roleID])

class LinkCog(Cog): # Cogs have to inherit from the commands.Cog
    def __init__(self, bot) -> None:
        self.bot = bot
        self.github_regex = re.compile(r'https:\/\/github\.com\/([a-zA-Z0-9-]+)\/([a-zA-Z0-9-]+)(\/(((tree|blob)\/[a-zA-Z0-9-]+)?(\/.*)?))?$')
        self.guild = discord.utils.get(bot.guilds, id = config.secrets['guild-id'])

    def eval_logic(self, discordID : int, link : str) -> Tuple[str, bool]:
        executeTime = time.time()
        if not re.findall(self.github_regex, link):
            return 'The given link is not a link to a github repo!', False

        # get the member from discordID
        member = mainTable.getMember(discordID=discordID)
        if not member:
            return f"You have not registed yet! Register in the server's welcome channel to use /eval.", False

        # get the manager assgined to this member
        manager = mainTable.getMember(rollno=member.groupManagerRollNo)

        if not manager:
            logs.log.error(f'Could not find manager for {member.rollno} with {member.groupManagerRollNo=}')
            return f'Error: Your manager was not found in database. This incident has been reported!\nTry again in a few hours.', False
    
        # get the manager's queue
        managerQueue = getMemberQueue(manager)
        print(managerQueue.pending_links)
        # build a new link
        newLink = QueueLink(managerQueue).add_layer(member.rollno, executeTime).set_link(link).set_time(executeTime)

        # add the link for review
        managerQueue.append_link(newLink)
        
        # return error if the link already exists
        if not newLink.valid:
            return f'The link {link} has already been queued to be reviewed by {manager.name}', False

        return f'Added link to queue for review by {manager.name}', True

    # assumes only roles that can have access to this
    # function use this
    def view_logic(self, discordID : int) -> Tuple[str, MemberInfo]:
        manager = mainTable.getMember(discordID=discordID)

        if not manager:
            logs.log.error(f'Could not find manager with {discordID=}')
            return f'Error: Manager with {discordID=} not registered!\nThis has been reported. Try again in a few hours', None

        managerQueue = getMemberQueue(manager)

        # pop previous viewing link
        managerQueue.pop_viewing_link()

        if managerQueue.link_sizes[QueueLink.PENDING] == 0:
            return f'All submitted reviews have been viewed!', None

        # pop a link to view
        currentLink = managerQueue.pop_pending_link()

        show_time = pretty_format_deltatime(time.time(), currentLink.layers[0][1])

        student = mainTable.getMember(rollno=currentLink.layers[0][0])

        # view message
        msg  = f'Student: {student.name} [submitted {show_time}]\n'
        
        # if this message was approved, then show the highest level of
        # approval
        if len(currentLink.layers) > 1:
            topLvlManager = mainTable.getMember(rollno=currentLink.layers[-1][0])
            approve_time = pretty_format_deltatime(time.time(), currentLink.layers[-1][1])
            msg += f'Approved by: {topLvlManager.name} {approve_time}\n'

        msg += f'link: {currentLink.link}\n'

        return msg, student
    
    # approve, and escalate to higher level
    # assumes only roles that can have access to this
    # function use this
    def approve_logic(self, discordID : int) -> Tuple[str, bool]:
        executeTime = time.time()
        manager = mainTable.getMember(discordID=discordID)
        
        if not manager:
            logs.log.error(f'Could not find manager with {discordID=}')
            return f'Error: Manager with {discordID=} not registered!\nThis has been reported. Try again in a few hours', False
        
        managerQueue = getMemberQueue(manager)
        
        currentLink : QueueLink | None = None
        
        if managerQueue.link_sizes[QueueLink.VIEWING] > 0:
            currentLink = managerQueue.viewing_links[0]
        else:
            return f'You are not reviewing any link currently', False
        
        # get the higher level
        executive = mainTable.getMember(rollno=manager.groupManagerRollNo)
        
        if not executive:
            logs.log.error(f'Could not find executive with {manager.groupManagerRollNo=}')
            return f'Error: Manager with {manager.groupManagerRollNo=} not registered!\nThis has been reported. Try again in a few hours', False
        
        executiveQueue = getMemberQueue(executive)
        
        forwarded_link = QueueLink(executiveQueue).from_queueLink(currentLink).add_layer(manager.rollno, executeTime).set_time(executeTime)
        
        executiveQueue.append_link(forwarded_link)
        
        student = mainTable.getMember(rollno=currentLink.layers[0][0])
        
        # return error if the link already exists
        if not forwarded_link.valid:
            return f'You have already approved the link:{currentLink.link} from {student.name}', False
        
        return f'link from {student.name} has been approved for review by {executive.name}', True

    # returns no. of people pending to view
    # currently viewing, etc.
    def view_status_logic(self, discordID : int) -> Tuple[str, bool]:
        manager = mainTable.getMember(discordID=discordID)
        
        if not manager:
            logs.log.error(f'Could not find manager with {discordID=}')
            return f'Error: Manager with {discordID=} not registered!\nThis has been reported. Try again in a few hours', False
        
        managerQueue = getMemberQueue(manager)
        
        msg  = f'Viewed links: {managerQueue.link_sizes[QueueLink.VIEWED]}\n'
        msg += f'Pending links: {managerQueue.link_sizes[QueueLink.PENDING]}'
        
        if managerQueue.link_sizes[QueueLink.VIEWING] > 0:
            currentLink = managerQueue.viewing_links[0]
            student = mainTable.getMember(rollno=currentLink.layers[0][0])
            msg += f'\nViewing: {currentLink.link} by {student.name}'
        
        return msg, True

    @app_commands.command(name='eval', description='Submit your assignment to your TA/PM')
    async def eval(self, interaction : Interaction, link : str):
        logs.cmd.info(f'{interaction.user.name}({interaction.user.id}) used /eval({link=})')
        
        msg, success = self.eval_logic(interaction.user.id, link=link)
        
        try:
            await interaction.response.send_message(msg, ephemeral=(interaction.guild != None))
        except Exception as e:
            logs.log.error('Error: Fatal Exception occured in eval: %s', e, exc_info=True)
            
    @app_commands.command(name='view', description='Look at the submissions from students')
    async def view(self, interaction : Interaction):
        logs.cmd.info(f'{interaction.user.name} used /view.')
        
        msg, student = self.view_logic(interaction.user.id)
        
        try:
            if student:
                manager = mainTable.getMember(discordID=interaction.user.id)
                if config.isRoleChannelDM(manager.roleID):
                    lname = student.name.strip().lower().replace(' ', '-')
                    channel = get(self.guild.channels, name=f'{lname}-{student.rollno}-{manager.roleID}')
                    msg += f'Channel: {channel.mention}'
                else:
                    student = get(self.guild.members, id=student.discordID)
                    msg += f'DM: {student.mention}'
            
            await interaction.response.send_message(msg, ephemeral=(interaction.guild != None))
        except Exception as e:
            logs.log.error('Error: Fatal Exception occured in view: %s', e, exc_info=True)
    
    @app_commands.command(name='viewstats', description='Get the number of completed and pending reviews left')
    async def viewstats(self, interaction : Interaction):
        logs.cmd.info(f'{interaction.user.name}({interaction.user.id}) used /viewstats.')
        
        msg, success = self.view_status_logic(interaction.user.id)
        
        try:
            await interaction.response.send_message(msg, ephemeral=(interaction.guild != None))
        except Exception as e:
            logs.log.error('Error: Fatal Exception occured in viewstats: %s', e, exc_info=True)
    
    @app_commands.command(name='approve', description='Sends the current viewing link to GVV Sir')
    async def approve(self, interaction : Interaction):
        logs.cmd.info(f'{interaction.user.name}({interaction.user.id}) used /approve.')
        
        msg, success = self.approve_logic(interaction.user.id)
        
        try:
            await interaction.response.send_message(msg, ephemeral=(interaction.guild != None))
        except Exception as e:
            logs.log.error('Error: Fatal Exception occured in approve: %s', e, exc_info=True)


