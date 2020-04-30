"""
Animal Crossing New Horizons Island Queue Discord Bot
Author: Marshall Jankovsky
github.com/marshalltj/island-queue-bot

Version: 1.2.0

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

#---Env/Constants setup---#
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') #your bot token

try:
    TURNIP_CHANNEL = int(os.getenv('TURNIP_CHANNEL')) #id of the channel you want it to send turnip queue messages to
except ValueError:
    TURNIP_CHANNEL = None

try:
    GENERAL_CHANNEL = int(os.getenv('GENERAL_CHANNEL')) #id of the channel you want it to send normal queue messages to
except ValueError:
    GENERAL_CHANNEL = None

bot = commands.Bot(command_prefix=helpMessages.COMMAND_PREFIX, case_insensitive=True)
bot.remove_command('help')

DEBUG = False #flag to disable some restrictions when debugging
ISLANDS = [] #global list containing all active island queues

#on_ready override
#When the bot spins up, log information about the server it's connected to.
@bot.event
async def on_ready():
    print(f"{bot.user} is up and running.\nConnected to {bot.guilds[0]}\nSending turnip queues to {TURNIP_CHANNEL}\nSending general queues to {GENERAL_CHANNEL}")
    await bot.change_presence(activity=discord.Game(f"{helpMessages.COMMAND_PREFIX}help | github.com/marshalltj/island-queue-bot"))

#---Helper Funtions---#

#Searches an Island owned by an <owner>
#Parameters: <owner : discord.User>
#Returns the Island or None if not found
def getIslandByOwner(owner):
    for island in ISLANDS:
        if island.owner == owner:
            return island

#Seaches for an Island by its unique <islandId> generated from createIslandId()
#Parameters: <islandId : str>
#Returns the Island or None if not found
def getIslandById(islandId):
    for island in ISLANDS:
        if island.islandId == islandId:
            return island  

#Creates a random and unique 3 digit island ID
#Returns the islandId as a str
def createIslandId():
    islandId = f'{random.randrange(1, 10**3):03}'
    if getIslandById(islandId) == None:
        return islandId
    else: #ID already exists, try again
        return createIslandId()

#Checks if a <user> has admin permissions on the server
#Paramters: <user : discord.User>
#Returns: True if the user has admin permissions, False otherwise
def isUserAdmin(user):
    member = bot.guilds[0].get_member(user.id)
    if member == None:   
        return False

    for role in member.roles:
        if role.permissions.administrator:
            return True

    return False

#---Bot Commands---#

#Command that creates an Island object and adds it to the list of ISLANDS then sends messages letting users know an island queue has been created.
#Parameters: <ctx : discord.ext.commands.Context> <price : int> <queueSize : int>
@commands.dm_only()
@bot.command(name='create')
async def createQueue(ctx, code, price: int = None, queueSize: int = 3):
    owner = ctx.message.author

    if getIslandByOwner(owner) != None:
        await ctx.send("Please close your current queue before opening another.")
        return

    #user provided 2 arguements but second is too small to be a price, so must be a queueSize
    if price != None and price < 8:
        queueSize = price
        price = None

    if queueSize > 7 or queueSize < 1:
        await ctx.send("Please enter a valid queue size (1-7).")
        return

    ISLANDS.append(Island(owner, price, code, createIslandId(), queueSize))
    newIsland = getIslandByOwner(owner)

    #check if island was successfully created
    if newIsland == None:
        await ctx.send("Failed to create queue for island.")
        print("Failed to create island for", owner)
        return

    print("Created new island queue for", owner, "id:", newIsland.islandId)
    await ctx.send(f"Island queue created with ID: island{newIsland.islandId}. Use {helpMessages.COMMAND_PREFIX}close to delete your island queue.")

    #determine which channel to send to based on if a price was provided
    if price != None:
        if datetime.datetime.today().weekday() == 6:
            buySellStr = "buy"
        else:
            buySellStr = "sell"

        if TURNIP_CHANNEL != None:
            await bot.get_channel(TURNIP_CHANNEL).send(
                f"{owner.name} has a queue to visit their island to {buySellStr} turnips for {newIsland.price} bells! Use '{helpMessages.COMMAND_PREFIX}join island{newIsland.islandId} <number of trips>' to be added to the queue!"
            )

    elif GENERAL_CHANNEL != None:
        await bot.get_channel(GENERAL_CHANNEL).send(
            f"{owner.name} has a queue to visit their island! Use '{helpMessages.COMMAND_PREFIX}join island{newIsland.islandId} <number of trips>' to be added to the queue!"
        )

#Command that deletes an Island object from the list of ISLANDS
#Parameters: <islandId : str>
@bot.command(name='close')
async def closeQueue(ctx, islandId : str = None):
    owner = ctx.message.author
    island = getIslandByOwner(owner)
    admin = None

    if islandId != None: #admin closure
        island = getIslandById(islandId[-3:])

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

#Command to update a dodo code for an Island. Messages users who were allowed on the new code.
#Paramters: <ctx : discord.ext.commands.Context> <code : str>
@commands.dm_only()
@bot.command(name='update')
async def updateQueue(ctx, code):
    owner = ctx.message.author
    island = getIslandByOwner(owner)

    if island == None:
        await ctx.send(f"{owner}, you do not have any open islands.")
        return

    island.code = code

    if island.getNumVisitors() < island.queueSize:
        dmLen = island.getNumVisitors()
    else:
        dmLen = island.queueSize

    await ctx.send(f"{owner}, your Dodo code has been updated to {island.islandId}. {dmLen} users will be messaged with the updated code.")
    print("Updated Dodo code for island", island.islandId, "Messaging", dmLen, "users updated dodo code for island.")

    for i in range(dmLen):
        visitor = island.visitors[i].user
        await visitor.create_dm()
        await visitor.dm_channel.send(
            f"Hello {visitor.name}, {owner} has updated their Dodo code. Use {island.code} to visit their island instead of the previous code. Remember to use '{helpMessages.COMMAND_PREFIX}leave {island.islandId}' when you're done and off their island."
        )

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
@bot.command(name="islands")
async def listIslands(ctx):
    islandStr = f"Currently {len(ISLANDS)} open."

    if len(ISLANDS) > 0:
        islandStr += "\n\n```------------------------------"
        for island in ISLANDS:
            islandStr += f"\nOwner: {island.owner.name} | ID: island{island.islandId}"

            if island.price != None:
                islandStr += f" | Bell Price: {island.price}" 

            islandStr += f" | Users in queue: {island.getNumVisitors()}"

        islandStr += f"```\n\nIsland there that isn't open? Tell the owner to use '{helpMessages.COMMAND_PREFIX}close' to close their island."
    islandStr += f"\nCreate a queue for your own island by messaging this bot '{helpMessages.COMMAND_PREFIX}create <dodo code>'"
    await ctx.send(islandStr)

#--Error Handling---#    

@createQueue.error
async def createError(ctx, error):
    if isinstance(error, commands.PrivateMessageOnly):
        await ctx.send("Create can only be exectued by directly messaging the bot - please create a new dodo code and try again by messaging this bot directly.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Looks like you may have mixed up the Dodo code and price - use '{helpMessages.COMMAND_PREFIX}help create' to see usage")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Looks like you're missing an argument - use '{helpMessages.COMMAND_PREFIX}help create' to see usage")
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

@updateQueue.error
async def updateError(ctx, error):
    if isinstance(error, commands.PrivateMessageOnly):
        await ctx.send("Update can only be exectued by directly messaging the bot - please create a new dodo code and try again by messaging this bot directly.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Looks like you're missing the new Dodo code - use '{helpMessages.COMMAND_PREFIX}update <dodo code>'")
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
    if com != None:
        com = com.lower()

    if com == None:
        helpStr = helpMessages.MENU

    elif com == "create":
        helpStr = helpMessages.CREATE

    elif com == "close":
        helpStr = helpMessages.CLOSE

    elif com == "remove":
        helpStr = helpMessages.REMOVE

    elif com == "update":
        helpStr = helpMessages.UPDATE

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
