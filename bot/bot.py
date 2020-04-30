"""
Animal Crossing New Horizons Island Queue Discord Bot
Author: Marshall Jankovsky
github.com/marshalltj/island-queue-bot

Version: 2.0.0

bot.py is a discord.ext.commands.Bot implementation for setup, connections and commands as well as error handling.
"""

import os
import datetime
import discord
import helpMessages
import random

from discord.ext import commands
from dotenv import load_dotenv
from island import Island
from server import Server

#---Env/Constants setup---#
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') #bot token

try:
    TURNIP_CHANNEL = int(os.getenv('TURNIP_CHANNEL')) #id of the channel you want it to send turnip queue messages to
except ValueError:
    TURNIP_CHANNEL = None

try:
    GENERAL_CHANNEL = int(os.getenv('GENERAL_CHANNEL')) #id of the channel you want it to send normal queue messages to
except ValueError:
    GENERAL_CHANNEL = None

bot = commands.Bot(command_prefix=helpMessages.COMMAND_PREFIX)
bot.remove_command('help')

DEBUG = False #flag to disable some restrictions when debugging
ISLANDS = [] #global list containing all active island queues - SUNSET THIS
SERVERS = [] #global list containing all guilds the bot is connected to

#---Helper Funtions---#

#Searches all Servers for an Island owned by <owner>
#Parameters: <owner : discord.User>
#Returns the Island or None if not found
def getIslandByOwner(owner):
    for server in SERVERS:
        for island in server.islands:
            if island.owner == owner:
                return island

#Searches a <server> for an Island owned by <owner>
#Parameters: <owner : discord.User> <server : Server>
#Returns the Island or None if not found
def getIslandByOwnerInServer(owner, server):
    for island in server.islands:
        if island.owner == owner:
            return island

#Seaches for all Servers for an Island by its unique <islandId> generated from createIslandId()
#Parameters: <islandId : str>
#Returns the Island or None if not found
def getIslandById(islandId):
    for server in SERVERS:
        for island in server.islands:
            if island.islandId == islandId:
                return island  

#Searches a <server> for an Island with an <islandId>
#Parameters: <islandId : str> <server : Server>
#Returns the Island or None if not found
def getIslandByIdInServer(islandId, server):
    for island in server.islands:
        if island.islandId == islandId:
            return island

#Creates a random and unique 4 digit island ID
#Returns the islandId as a str
def createIslandId():
    islandId = f'{random.randrange(1, 10**4):04}'
    if getIslandById(islandId) == None:
        return islandId
    else: #ID already exists, try again
        return createIslandId()

#Checks if a <user> has admin permissions in <guild>
#Paramters: <user : discord.User> <guild : discord.Guild>
#Returns: True if the user has admin permissions, False otherwise
def isUserAdmin(user):
    member = bot.guilds[0].get_member(user.id)
    if member == None:   
        return False

    for role in member.roles:
        if role.permissions.administrator:
            return True

    return False

#Creates a Server object and adds it to the list of servers if it's not already in the list
#Parameters: <guild : discord.Guild>
def addServer(guild):
    for server in SERVERS:
        if server.guild == guild:
            return 
    SERVERS.append(Server(guild))


#Gets the Server associated with a <guild>
#Parameters: <guild : discord.Guild>
def getServerByGuild(guild):
    for server in SERVERS:
        if server.guild == guild:
            return server

#---Events---#

#on_ready override
#When the bot spins up, log information about the server it's connected to.
@bot.event
async def on_ready():
    print(f"{bot.user} is up and running.\nConnected to {len(bot.guilds)} servers")
    await bot.change_presence(activity=discord.Game(f"{helpMessages.COMMAND_PREFIX}help | github.com/marshalltj/island-queue-bot"))
    for guild in bot.guilds:
        addServer(guild)

#on_guild_join override
#When bot joins a guild, add that guild to the list of servers
@bot.event
async def on_guild_join(guild):
    addServer(guild)
    print("Bot added to server", guild)

#on_guild_remove override
#When bot leaves a guild, remove that guild from the list of servers
@bot.event
async def on_guild_remove(guild):
    for server in SERVERS:
        if server.guild == guild:
            print("Bot removed from server", guild)
            SERVERS.remove(server)
            return 

#---Managing Queue Commands---#

#Command that creates an Island object. 
#Parameters: <ctx : discord.ext.commands.Context> <price : int>
@commands.guild_only()
@bot.command(name='create')
async def createIsland(ctx, price: int = None):
    owner = ctx.message.author
    guild = ctx.guild

    island = getIslandByOwner(owner)
    if island != None:
        if island.code != None:
            await ctx.send(f"{owner.display_name}, please close your current queue before opening another.")
        else:
            await ctx.send("{owner.display_name}, you have already created an island. DM this bot with {helpMessages.COMMAND_PREFIX}open <dodo code> to open a queue for your island.")
        return

    server = getServerByGuild(guild)
    server.islands.append(Island(owner, price, createIslandId(), guild))

    newIsland = getIslandByOwnerInServer(owner, server)

    #check if island was successfully created
    if newIsland == None:
        await ctx.send("Failed to create queue for island.")
        print("Failed to create island for", owner)
        return

    print("Created new island queue for", owner, "id:", newIsland.islandId, "on server", newIsland.guild)
    await ctx.send(f"Island created with ID: {newIsland.islandId}. DM this bot with {helpMessages.COMMAND_PREFIX}open <dodo code> to open a queue for your island.")

#Command that opens the queue for an Island that has been created.
#Parameters: <ctx : discord.ext.commands.Context> <queueSize : int>
@commands.dm_only()
@bot.command(name='open')
async def openQueue(ctx, code, queueSize : int = 3):
    owner = ctx.message.author
    island = getIslandByOwner(owner)

    if island == None:
        await ctx.send(f"Please use {helpMessages.COMMAND_PREFIX}create to create an island before opening its queue.")
        return

    if island.code != None:
        await ctx.send(f"You already have an open queue. Use {helpMessages.COMMAND_PREFIX}close to close it.")
        return

    island.queueSize = queueSize
    island.code = code
    server = getServerByGuild(island.guild)
    await ctx.send(f"Your island queue is now open. Users can join the queue using {helpMessages.COMMAND_PREFIX}join {island.islandId}.")
    print("Opening the queue for island", island.islandId, "on server", island.guild)

    if island.price != None:
        if datetime.datetime.today().weekday() == 6:
            buySellStr = "buy"
        else:
            buySellStr = "sell"

        if server.turnipChannel != None:
            await bot.get_channel(server.turnipChannel).send(
                f"{owner.name} has a queue to visit their island to {buySellStr} turnips for {island.price} bells! Use '{helpMessages.COMMAND_PREFIX}join {island.islandId} <number of trips>' to be added to the queue!"
            )        

    elif server.generalChannel != None:
        await bot.get_channel(server.generalChannel).send(
            f"{owner.name} has a queue to visit their island! Use '{helpMessages.COMMAND_PREFIX}join {island.islandId} <number of trips>' to be added to the queue!"
        )

#Command that deletes an Island object from the list of ISLANDS
#Parameters: <islandId : str>
@commands.guild_only()
@bot.command(name='close')
async def closeQueue(ctx, islandId : str = None):
    owner = ctx.message.author
    server = getServerByGuild(ctx.guild)
    island = getIslandByOwnerInServer(owner, server)
    admin = None

    if islandId != None: 
        island = getIslandByIdInServer(islandId, server)

        if island == None:
            await ctx.send(f"{owner.name}, {islandId} is not a valid island ID.")
            return

        if isUserAdmin(owner):
            admin = owner
            owner = island.owner

        elif island.owner != owner:
            await ctx.send(f"{owner.name}, you don't have permission to close someone else's queue.")
            return

    if island == None:
        await ctx.send(f"{owner.name}, you have no open queues.")
        return
    
    removedIslandID = island.islandId
    islandPrice = island.price

    if admin != None:
        closedStr = f"{admin.name} has closed {owner.name}'s island queue."
    else:
        closedStr = f"{owner.name} has closed their island queue."

    #collect remaining users in queue
    if island.getNumVisitors() > 0:
        closedStr +=  " The following users were still in line:"
        for i in range(island.getNumVisitors()):
            closedStr += f"\n{i+1}: {island.visitors[i].user.name}"
    
    ISLANDS.remove(island)

    #check if island was successfully deleted
    if getIslandByOwner(owner) != None:
        await ctx.send(f"Failed to close queue for {owner.name}")
        print("Failed to delete island queue for", owner, "id:", removedIslandID)
        return

    #determine which channel to send closed message to
    if islandPrice != None:
        if TURNIP_CHANNEL != None and ctx.message.channel.id != TURNIP_CHANNEL:
            await bot.get_channel(TURNIP_CHANNEL).send(closedStr)

    elif GENERAL_CHANNEL != None and ctx.message.channel.id != GENERAL_CHANNEL:
        await bot.get_channel(GENERAL_CHANNEL).send(closedStr)

    await ctx.send(closedStr)

    if admin != None:
        await owner.create_dm()
        await owner.dm_channel.send(f"Hello {owner.name}, {admin.name} has closed your island queue.")
        print("Admin", admin, "deleted island queue for island id:", removedIslandID)
    else:
        print("Deleted island queue for", owner, "id:", removedIslandID)
        
#Command to remove a Visitor in <position> of a queue from an Island and then message the user that they were removed.
#Parameters: <ctx : discord.ext.commands.Context> <position : int> <islandId : str>
@bot.command(name='remove')
async def removeUser(ctx, position : int, islandId: str = None):
    owner = ctx.message.author
    idx = position - 1

    if islandId != None: #admin removal 
        if isUserAdmin(owner):
            island = getIslandById(islandId[-3:])
            if island == None:
                await ctx.send(f"{owner.name}, {islandId} is not a valid island ID.")
                return
        else:
            await ctx.send(f"{owner.name}, you don't have permission to remove someone else from a queue.")
            return

    else:
        island = getIslandByOwner(owner)
        if island == None:
            await ctx.send(f"{owner.name}, you do not currently have any open islands.")
            return

    if idx < 0 or idx >= island.getNumVisitors():
        await ctx.send(f"{position} is not a valid position in the queue. Use {helpMessages.COMMAND_PREFIX}queue island{island.islandId} to see who's in line currently.")
        return

    removedUser = island.popVisitor(idx).user 

    #check if Visitor was successfully removed
    if island.getUserPositionInQueue(removedUser) != -1:
        await ctx.send(f"Failed to remove {removedUser.name} from {owner.name}'s queue.")
        print("Failed to remove", removedUser, "from island", island.islandId)
        return

    await removedUser.create_dm()
    await removedUser.dm_channel.send(
        f"Hello {removedUser.name}, {owner.name} has removed you from the island queue for island{island.islandId}, most likely due to you forgetting to leave the queue after finishing up on the island."
    )

    await ctx.send(f"{owner.name} has removed {removedUser.name} from their island queue.")
    print(owner, "has removed", removedUser, "from island ID:", island.islandId, "from position", position, island.getNumVisitors(), "remaining in queue.")

    #message next user in line the dodo code
    if idx < island.queueSize and island.getNumVisitors() >= island.queueSize:
        newVisitor = island.visitors[island.queueSize-1]

        await newVisitor.user.create_dm()
        await newVisitor.user.dm_channel.send(
            f"Hello {newVisitor.user.name}, it's your turn to go to {island.owner.name}'s island! Use the Dodo code '{island.code}' to fly, and be sure to leave the queue with '{helpMessages.COMMAND_PREFIX}leave island{island.islandId}' once you are done and completely off the island."
        )

        newVisitor.setTimestamp()
        print("Messaging", newVisitor.user, "to allow them on island ID", island.islandId, "user queue position:", island.getUserPositionInQueue(newVisitor.user) + 1)

#--- Participating in Queue Commands ---#

#Command to add a Visitor to an Island
#Paramters: <ctx : discord.ext.commands.Context> <islandId : str> <trips : int>
@bot.command(name='join')
async def joinQueue(ctx, islandId, trips : int = 0):
    user = ctx.message.author
    island = getIslandById(islandId[-3:])

    if island == None:
        await ctx.send(f"{user.name}, {islandId} is not a valid island ID.")
        return

    if DEBUG == False and island.owner == user:
        await ctx.send(f"{user.name}, you can't join the queue for your own island.")
        return

    queuePosition = island.getUserPositionInQueue(user)

    if queuePosition != -1:
        await ctx.send(f"{user.name}, you are already in the queue at position {queuePosition + 1} out of {island.getNumVisitors()}.")
        return

    island.addVisitor(user, trips)
    queuePosition = island.getUserPositionInQueue(user)

    #check if Visitor was sucessfully added
    if queuePosition == -1:
        await ctx.send(f"Failed to add {user.name} to {island.owner.name}'s queue.")
        print("Failed to add", user, "to island", island.id)
        return

    print("User", user, "has joined the queue for island", island.islandId, "in position", queuePosition + 1, "out of", island.getNumVisitors())
    await ctx.send(f"{user.name}, you have been added to the queue for {island.owner.name}'s island and are currently in position {queuePosition + 1}. A DM will be sent to you from this bot with the Dodo code when it's your turn to visit the island.")

    #message user the dodo code if allowed on the island
    if queuePosition < island.queueSize:
        await user.create_dm()
        await user.dm_channel.send(
            f"Hello {user.name}, it's your turn to go to {island.owner.name}'s island! Use the Dodo code '{island.code}' to fly, and be sure to leave the queue with '{helpMessages.COMMAND_PREFIX}leave island{island.islandId}' once you are done and completely off the island."
        )
        print("Messaging", user, "to allow them on island ID", island.islandId, "user queue position:", island.getUserPositionInQueue(user) + 1)

#Command to remove a Visitor from an Island
#Parameters: <ctx : discord.ext.commands.Context> <islandId : str>
@bot.command(name='leave')
async def leaveQueue(ctx, islandId):
    user = ctx.message.author
    island = getIslandById(islandId[-3:])

    if island == None:
        await ctx.send(f"{user.name}, {islandId} is not a valid island ID.")
        return

    queuePosition = island.getUserPositionInQueue(user)

    if queuePosition == -1:
        await ctx.send(f"{user.name}, you are not currently in the queue for {island.owner.name}'s island.")
        return

    removed = island.removeUser(user)

    #check if Visitor was successfully removed
    if removed == False or island.getUserPositionInQueue(user) != -1:
        await ctx.send(f"Failed to remove {user.name} from {island.owner.name}'s queue.")
        print("Failed to remove", user, "from island", island.islandId)
        return

    await ctx.send(f"Thanks {user.name}, you've been removed from the queue for {island.owner.name}'s island!")
    print("Removed", user, "from queue for island", island.islandId, "from position", queuePosition + 1, island.getNumVisitors(), "remaining in line.")

    #message next user in line the dodo code
    if queuePosition < island.queueSize and island.getNumVisitors() >= island.queueSize:
        newVisitor = island.visitors[island.queueSize-1]
        await newVisitor.user.create_dm()
        await newVisitor.user.dm_channel.send(
            f"Hello {newVisitor.user.name}, it's your turn to go to {island.owner.name}'s island! Use the Dodo code '{island.code}' to fly, and be sure to leave the queue with '{helpMessages.COMMAND_PREFIX}leave island{island.islandId}' once you are done and completely off the island."
        )
        newVisitor.setTimestamp()
        print("Messaging", newVisitor.user, "to allow them on island ID", island.islandId, "user queue position:", island.getUserPositionInQueue(newVisitor.user) + 1)

@bot.command(name='dodo')
async def sendDodoCode(ctx, islandId):
    user = ctx.message.author
    island = getIslandById(islandId[-3:])

    if island == None:
        await ctx.send(f"{user.name}, {islandId} is not a valid island ID.")
        return

    queuePosition = island.getUserPositionInQueue(user)

    if queuePosition == -1:
        await ctx.send(f"{user.name}, you are not currently in the queue for {island.owner.name}'s island.")
        return

    if queuePosition >= island.queueSize:
        await ctx.send(f"{user.name}, it's not your turn to visit the island yet. Use '{helpMessages.COMMAND_PREFIX}queue {islandId}' to view the island's queue.")
        return

    await user.create_dm()
    await user.dm_channel.send(f"The Dodo code for {island.owner.name}'s island is '{island.code}'. Be sure to leave the queue with '{helpMessages.COMMAND_PREFIX}leave island{island.islandId}' once you are done and completely off the island.")
    print("Messaging", user, "Dodo code for island id", island.islandId, "via !dodo command")

#--- General Commands ---#

#Command to display information about an Island as well as each Visitor on the Island
#Parameters: <ctx : discord.ext.commands.Context> <islandId : str>
@bot.command(name='queue')
async def listQueue(ctx, islandId):
    island = getIslandById(islandId[-3:])

    if island == None:
        await ctx.send(f"{ctx.message.author.name}, {islandId} is not a valid island ID.")
        return

    queue = f"```Owner: {island.owner.name} | ID: {islandId}"

    if island.price != None:
        queue+= f" | Bell Price: {island.price}"

    queue += f" | Users in queue: {island.getNumVisitors()}\n{island.queueSize} users allowed on this island at a time."

    if island.getNumVisitors() > 0:
        queue += f"\n------------------------------"
        for i in range(island.getNumVisitors()):
            if i == island.queueSize:
                queue += "\n------------------------------"
            queue += f"\n{i + 1}: {island.visitors[i].user.name}    {island.visitors[i].trips} trips"
            if i < island.queueSize:
                queue += f"    {island.visitors[i].getTimeSpent()} minutes"

    queue += f"```\n\nUse '{helpMessages.COMMAND_PREFIX}join {islandId} <number of trips>' to join this queue."

    await ctx.send(queue)

#Command to list all Islands in ISLANDS and information about them
@bot.command(name='islands')
async def listIslands(ctx):
    islandStr = f"Currently {len(ISLANDS)} open."

    if len(ISLANDS) > 0:
        islandStr += "\n\n```"
        for island in ISLANDS:
            islandStr += f"\nOwner: {island.owner.name} | ID: island{island.islandId}"

            if island.price != None:
                islandStr += f" | Bell Price: {island.price}" 

            islandStr += f" | Users in queue: {island.getNumVisitors()}"

        islandStr += f"```\n\nIsland there that isn't open? Tell the owner to use '{helpMessages.COMMAND_PREFIX}close' to close their island."
    islandStr += f"\nCreate a queue for your own island by messaging this bot '{helpMessages.COMMAND_PREFIX}create <dodo code>'"
    await ctx.send(islandStr)

#--- Server Admin Commands ---#

@commands.has_guild_permissions(administrator=True)
@bot.command(name='setTurnipChannel')
async def setTurnipChannel(ctx):
    server = getServerByGuild(ctx.guild)

    server.turnipChannel = ctx.channel.id

    await ctx.send(f"Turnip Channel set to {ctx.channel}.")

@commands.has_guild_permissions(administrator=True)
@bot.command(name='setGeneralChannel')
async def setGeneralChannel(ctx):
    server = getServerByGuild(ctx.guild)

    server.generalChannel = ctx.channel.id

    await ctx.send(f"General Channel set to {ctx.channel}.")

#--- Bot Owner Commands ---#

@commands.is_owner()
@bot.command(name='listServers')
async def listServers(ctx):
    serverStr = f"Currently connected to {len(SERVERS)}."

    if len(SERVERS) > 0:
        serverStr += "\n\n```"
        for server in SERVERS:
            serverStr += f"\n{server.guild} | {len(server.islands)} islands"
        serverStr += "```"
    await ctx.send(serverStr)

#--Error Handling---#    

@createIsland.error
async def createError(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send(f"Looks like you didn't give a number for the <price> - use an integer like '500', don't type it out 'five-hundred'.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Looks like you're missing an argument - use '{helpMessages.COMMAND_PREFIX}help create' to see usage.")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send("This command can't be called in a DM.")
    else:
        raise

@openQueue.error
async def openError(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Looks like you're missing an argument - use '{helpMessages.COMMAND_PREFIX}help open' to see usage.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Looks like you didn't give a number for the <queue size> - use an integer like '4', don't type it out 'four'.")
    elif isinstance(error, commands.PrivateMessageOnly):
        await ctx.send(f"{helpMessages.COMMAND_PREFIX}open can only be exectued by directly messaging the bot - please create a new dodo code and try again by messaging this bot directly.")
    else:
        raise

@removeUser.error
async def removeError(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Looks like you didn't give a number for the position - use an integer like '4', don't type it out.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Looks like you're missing an argument - use '{helpMessages.COMMAND_PREFIX}remove <position>'")
    else:
        raise

@joinQueue.error
async def joinError(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Looks like you're missing an argument - use '{helpMessages.COMMAND_PREFIX}join <island ID>'")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Looks like you didn't give a number for your number of trips - use an integer like '4', don't type it out.")
    else:
        raise

@leaveQueue.error
async def leaveError(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Looks like you're missing an argument - use '{helpMessages.COMMAND_PREFIX}leave <island ID>'")
    else:
        raise

@sendDodoCode.error
async def dodoError(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Looks like you're missing an argument - use '{helpMessages.COMMAND_PREFIX}dodo <island ID>'")
    else:
        raise

@listQueue.error
async def leaveError(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Looks like you're missing an argument - use '{helpMessages.COMMAND_PREFIX}queue <island ID>'")
    else:
        raise

#---Help Menus---#  

#Command to display a general help menu or more information on a specified <com>
#Paramters <ctx : discord.ext.commands.Context> <com : str>
@bot.command()
async def help(ctx, com : str = None):
    if com == None:
        helpStr = helpMessages.MENU

    elif com == "create":
        helpStr = helpMessages.CREATE

    elif com == "close":
        helpStr = helpMessages.CLOSE

    elif com == "remove":
        helpStr = helpMessages.REMOVE

    elif com == "join":
        helpStr = helpMessages.JOIN

    elif com == "leave":
        helpStr = helpMessages.LEAVE

    elif com == "dodo":
        helpStr = helpMessages.DODO

    elif com == "islands":
        helpStr = helpMessages.ISLANDS

    elif com == "queue":
        helpStr = helpMessages.QUEUE

    else:
        helpStr = f"{com} is not a valid command. Use '{helpMessages.COMMAND_PREFIX}help' to list this bot's available commands."

    await ctx.send(helpStr)

bot.run(TOKEN)