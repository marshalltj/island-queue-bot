"""
Animal Crossing New Horizons Island Queue Discord Bot
Author: Marshall Jankovsky
github.com/marshalltj/island-queue-bot

Version: 2.0.0

bot.py is a discord.ext.commands.Bot implementation for setup, connections and commands as well as error handling.
"""

import os
import discord
import helpMessages
import random
import asyncio
import logging
import mysql.connector

from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
from island import Island
from server import Server

DEBUG = False #flag to disable some restrictions when debugging

#---Env/Constants setup---#
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') #bot token
DB_HOST = os.getenv('DB_HOST') #database host
DB_USER = os.getenv('DB_USER') #database user
DB_PW = os.getenv('DB_PW') #database password
DB_NAME = os.getenv('DB_NAME') #database name

bot = commands.Bot(command_prefix=helpMessages.COMMAND_PREFIX, case_insensitive=True)
bot.remove_command('help')

logFileName = '../logs/' + str(datetime.now().strftime('%m_%d_%y_%I_%M')) + '.log'
if DEBUG:  
    logFileName = "../logs/log.log"
logging.basicConfig(format='%(asctime)s: %(message)s', filename=logFileName, filemode='w', level=logging.INFO, datefmt='%m-%d-%y %H:%M:%S')
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
logging.getLogger("").addHandler(console)

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
def isUserAdmin(user, guild):
    member = guild.get_member(user.id)
    if member == None:   
        return False

    for role in member.roles:
        if role.permissions.administrator:
            return True

    return False

#Gets the Server associated with a <guild>
#Parameters: <guild : discord.Guild>
def getServerByGuild(guild):
    for server in SERVERS:
        if server.guild == guild:
            return server

def sqlConnection():
    return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PW,
            database=DB_NAME
        )

async def messageUser(visitor, island):
    await visitor.user.create_dm()
    await visitor.user.dm_channel.send(
        f"Hello {visitor.user.name}, it's your turn to go to {island.owner.name}'s island! Use the Dodo code '{island.code}' to fly, and be sure to leave the queue with '{helpMessages.COMMAND_PREFIX}leave {island.islandId}' once you are done and completely off the island."
    )
    visitor.setTimestamp()
    logging.info(f"Messaging {visitor.user} to allow them on island {island.islandId}. User queue position: {island.getUserPositionInQueue(visitor.user) + 1}")

#---Backround Tasks---#

async def clean():
    await bot.wait_until_ready()

    while True:
        logging.info("Starting Island/User clean.")
        for server in SERVERS:
            for island in server.islands:

                if island.getAge() >= 10: #close islands that have been open for more than 10 hrs
                    closedStr = f"Island {island.islandId} owned by {island.owner} is being closed since it has been active for more than 10 hours."

                    #collect remaining users in queue
                    if island.getNumVisitors() > 0:
                        closedStr +=  " The following users were still in line:"
                        for i in range(island.getNumVisitors()):
                            closedStr += f"\n{i+1}: {island.visitors[i].user.name}"

                    if island.price != None and server.turnipChannel != None:
                        await bot.get_channel(server.turnipChannel).send(closedStr) 

                    elif server.generalChannel != None:
                        await bot.get_channel(server.generalChannel).send(closedStr) 

                    await island.owner.create_dm()
                    await island.owner.dm_channel.send(
                        f"Your island {island.islandId} was closed due to being active for more than 10 hours. Please remember to use '{helpMessages.COMMAND_PREFIX}close' to close your island when you're done in the future."
                    )

                    logging.info(f"Island {island.islandId} has been closed due to inactivity.")

                    server.islands.remove(island)

                else: #remove users who have been allowed on an island more than alloted time set by server
                    removedUsers = []
                    if island.queueSize != None:
                        for i in range(island.queueSize):
                            if i < island.getNumVisitors() and island.visitors[i].getTimeSpent() >= server.timeout:
                                removedUsers.append(island.visitors[i])

                    for removedUser in removedUsers:
                        island.visitors.remove(removedUser)

                        await removedUser.user.create_dm()
                        await removedUser.user.dm_channel.send(
                            f"Hello {removedUser.user.name}, you have been removed from the queue {island.owner.name}'s island for being allowed on for over {server.timeout} minutes. Please remember to use '{helpMessages.COMMAND_PREFIX}leave <islandId>' once you're done in the future."
                        )

                        logging.info(f"{removedUser.user} has been removed due to inactivity from island {island.islandId} from position {i+1}. {island.getNumVisitors()} remaining in queue.")

                        #message next user in line the dodo code
                        if i < island.queueSize and island.getNumVisitors() >= island.queueSize:
                            await messageUser(island.visitors[island.queueSize-1], island)

        logging.info("Finished Island/User clean.")
        if DEBUG == True:
            await asyncio.sleep(150)
        else:
            await asyncio.sleep(300) #run every 5 min

#---Events---#

#on_ready override
#When the bot spins up, log information about the server it's connected to.
@bot.event
async def on_ready():
    logging.info(f"{bot.user} is up and running.\nConnected to {len(bot.guilds)} servers")
    await bot.change_presence(activity=discord.Game(f"{helpMessages.COMMAND_PREFIX}help | github.com/marshalltj/island-queue-bot"))
    for guild in bot.guilds:
        if getServerByGuild(guild) == None:
            db = sqlConnection()
            cursor = db.cursor()

            sql = f"SELECT * FROM Servers WHERE ID={guild.id}"
            cursor.execute(sql)
            if cursor.fetchone() == None:

                sql = f"INSERT INTO Servers (ID) VALUES ({guild.id})"
                cursor.execute(sql)
                db.commit()
                logging.info(f"Adding {guild} to databse.")

            else:
                logging.info(f"{guild} already present in database.")

            cursor.close()
            db.close()

            SERVERS.append(Server(guild, sqlConnection()))

#on_guild_join override
#When bot joins a guild, add that guild to the list of servers
@bot.event
async def on_guild_join(guild):
    if getServerByGuild(guild) == None:
        db = sqlConnection()
        cursor = db.cursor()

        sql = f"SELECT * FROM Servers WHERE ID={guild.id}"
        cursor.execute(sql)

        if cursor.fetchone() == None:
            sql = f"INSERT INTO Servers (ID) VALUES ({guild.id})"
            cursor.execute(sql)
            db.commit()
            logging.info(f"Adding {guild} to database.")

        else:
            logging.info(f"{guild} already present in database.")

        cursor.close()
        db.close()

        SERVERS.append(Server(guild, sqlConnection()))
        logging.info(f"Bot added to server {guild}.")

#on_guild_remove override
#When bot leaves a guild, remove that guild from the list of servers
@bot.event
async def on_guild_remove(guild):
    db = sqlConnection()
    cursor = db.cursor()
    sql = f"DELETE FROM Servers WHERE ID = {guild.id}"
    cursor.execute(sql, guild.id)
    db.commit()

    cursor.close()
    db.close()

    SERVERS.remove(getServerByGuild(guild))
    logging.info(f"Bot removed from server {guild}.")

#---Managing Queue Commands---#

#Command that creates an Island object. 
#Parameters: <ctx : discord.ext.commands.Context> <price : int>
@commands.guild_only()
@bot.command(name='create')
async def createIsland(ctx, price: int = None):
    owner = ctx.message.author
    server = getServerByGuild(ctx.guild)

    island = getIslandByOwnerInServer(owner, server)

    if island != None:
        if island.code != None:
            await ctx.send(
                f"{owner.display_name}, please use '{helpMessages.COMMAND_PREFIX}close' before opening another or '{helpMessages.COMMAND_PREFIX}update' to update it."
            )
        else:
            await ctx.send(
                f"{owner.display_name}, you have already created an island. DM this bot with {helpMessages.COMMAND_PREFIX}open <dodo code> to open a queue for your island."
            )
        return

    server.islands.append(Island(owner, price, createIslandId(), ctx.guild))

    newIsland = getIslandByOwnerInServer(owner, server)

    #check if island was successfully created
    if newIsland == None:
        await ctx.send("Failed to create queue for island.")
        logging.error(f"Failed to create island for {owner}.")
        return

    logging.info(f"Created new island queue for {owner}. ID: {newIsland.islandId} on server {newIsland.guild}.")
    await ctx.send(
        f"Island created with ID: {newIsland.islandId}. DM this bot with {helpMessages.COMMAND_PREFIX}open <dodo code> to open a queue for your island."
    )

#Command that opens the queue for an Island that has been created.
#Parameters: <ctx : discord.ext.commands.Context> <queueSize : int>
@commands.dm_only()
@bot.command(name='open')
async def openQueue(ctx, code, queueSize : int = 3):
    owner = ctx.message.author
    island = getIslandByOwner(owner)

    if island == None:
        await ctx.send(
            f"Please use {helpMessages.COMMAND_PREFIX}create to create an island before opening its queue."
        )
        return

    if island.code != None:
        await ctx.send(
            f"You already have an open queue. Use '{helpMessages.COMMAND_PREFIX}close' to close it or '{helpMessages.COMMAND_PREFIX}update' to update it."
        )
        return

    if queueSize < 1 or queueSize > 7:
        await ctx.send("Please provide a valid queue size (1-7).")
        return

    island.queueSize = queueSize
    island.code = code

    server = getServerByGuild(island.guild)

    await ctx.send(
        f"Your island queue is now open. Users can join the queue using '{helpMessages.COMMAND_PREFIX}join {island.islandId}'."
    )
    logging.info(f"Opening the queue for island {island.islandId} on server {island.guild}.")

    if island.price != None:
        if server.turnipChannel != None:
            await bot.get_channel(server.turnipChannel).send(
                f"{owner.name} has a queue to visit their island to move turnips for {island.price} bells! Use '{helpMessages.COMMAND_PREFIX}join {island.islandId} <number of trips>' to be added to the queue!"
            )        

    elif server.generalChannel != None:
        await bot.get_channel(server.generalChannel).send(
            f"{owner.name} has a queue to visit their island! Use '{helpMessages.COMMAND_PREFIX}join {island.islandId} <number of trips>' to be added to the queue!"
        )

#Command that deletes an Island object from the list of ISLANDS
#Parameters: <islandId : str>
@bot.command(name='close')
async def closeQueue(ctx, islandId : str = None):
    owner = ctx.message.author
    admin = None

    if islandId != None: 
        island = getIslandById(islandId)

        if island == None:
            await ctx.send(f"{owner.name}, {islandId} is not a valid island ID.")
            return

        if isUserAdmin(owner, island.guild):
            admin = owner
            owner = island.owner

        elif island.owner != owner:
            await ctx.send(f"{owner.name}, you don't have permission to close someone else's queue.")
            return

    else:
        island = getIslandByOwner(owner)

        if island == None:
            await ctx.send(f"{owner.name}, you have no open queues.")
            return

    server = getServerByGuild(island.guild)
    removedIslandID = island.islandId
    removedIslandPrice = island.price

    if admin != None:
        closedStr = f"{admin.name} has closed {owner.name}'s island queue."
    else:
        closedStr = f"{owner.name} has closed their island queue."

    #collect remaining users in queue
    if island.getNumVisitors() > 0:
        closedStr +=  " The following users were still in line:"
        for i in range(island.getNumVisitors()):
            closedStr += f"\n{i+1}: {island.visitors[i].user.name}"
    
    server.islands.remove(island)

    #check if island was successfully deleted
    if getIslandByOwnerInServer(owner, server) != None:
        await ctx.send(f"Failed to close queue for {owner.name}")
        logging.error(f"Failed to delete island queue for {owner} ID: {removedIslandID}.")
        return

    #determine which channel to send closed message to
    if removedIslandPrice != None:
        if server.turnipChannel != None and ctx.message.channel.id != server.turnipChannel:
            await bot.get_channel(server.turnipChannel).send(closedStr)

    elif server.generalChannel != None and ctx.message.channel.id != server.generalChannel:
        await bot.get_channel(server.generalChannel).send(closedStr)

    await ctx.send(closedStr)

    if admin != None:
        await owner.create_dm()
        await owner.dm_channel.send(f"Hello {owner.name}, {admin.name} has closed your island queue.")
        logging.info(f"Admin {admin} deleted island queue for island id: {removedIslandID}.")
    else:
        logging.info(f"Deleted island queue for {owner} ID: {removedIslandID}.")
        
#Command to remove a Visitor in <position> of a queue from an Island and then message the user that they were removed.
#Parameters: <ctx : discord.ext.commands.Context> <position : int> <islandId : str>
@bot.command(name='remove')
async def removeUser(ctx, position : int, islandId: str = None):
    owner = ctx.message.author
    idx = position - 1

    if islandId != None: #admin removal 
        island = getIslandById(islandId[-4:])

        if island == None:
            await ctx.send(f"{owner.name}, {islandId} is not a valid island ID.")
            return

        if isUserAdmin(owner, island.guild) == False and island.owner != owner:
            await ctx.send(f"{owner.name}, you don't have permission to remove someone else from a queue.")
            return            

    else:
        island = getIslandByOwner(owner)
        if island == None:
            await ctx.send(f"{owner.name}, you do not currently have any open islands.")
            return

    if idx < 0 or idx >= island.getNumVisitors():
        await ctx.send(
            f"{position} is not a valid position in the queue. Use {helpMessages.COMMAND_PREFIX}list {island.islandId} to see who's in line currently."
        )
        return

    removedUser = island.popVisitor(idx).user 

    #check if Visitor was successfully removed
    if island.getUserPositionInQueue(removedUser) != -1:
        await ctx.send(f"Failed to remove {removedUser.name} from {owner.name}'s queue.")
        logging.error(f"Failed to remove {removedUser} from island {island.islandId}.")
        return

    await removedUser.create_dm()
    await removedUser.dm_channel.send(
        f"Hello {removedUser.name}, {owner.name} has removed you from the island queue for island{island.islandId}, most likely due to you forgetting to leave the queue after finishing up on the island."
    )

    await ctx.send(f"{owner.name} has removed {removedUser.name} from their island queue.")
    logging.info(f"{owner} has removed {removedUser} from Island {island.islandId} from position {position}. {island.getNumVisitors()} remaining in queue.")

    #message next user in line the dodo code
    if idx < island.queueSize and island.getNumVisitors() >= island.queueSize:
        await messageUser(island.visitors[island.queueSize-1], island)

#Command to update a dodo code for an Island. Messages users who were allowed on the new code.
#Paramters: <ctx : discord.ext.commands.Context> <code : str>
@bot.command(name='update')
async def updateQueue(ctx, attribute, value):
    owner = ctx.message.author
    island = getIslandByOwner(owner)
    attribute = attribute.lower()

    if island == None:
        await ctx.send(f"{owner.name}, you do not have any open islands.")
        return

    if attribute == "dodo":

        if isinstance(ctx.message.channel, discord.DMChannel) == False:
            await ctx.send(f"Updating the Dodo code must be done in a DM. Please make a new code and message this bot.")
            return

        if island.code == None:
            await ctx.send(f"You haven't opened your queue yet - to set the Dodo code and open your Island use '{helpMessages.COMMAND_PREFIX}open <dodo code>'")
            return

        island.code = value

        if island.getNumVisitors() < island.queueSize:
            dmLen = island.getNumVisitors()
        else:
            dmLen = island.queueSize

        await ctx.send(
            f"{owner}, your Dodo code has been updated to {island.code}. {dmLen} users will be messaged with the updated code."
        )
        logging.info(f"Updated Dodo code for island {island.islandId}. Messaging {dmLen} users updated dodo code for island.")

        for i in range(dmLen):
            visitor = island.visitors[i].user
            await visitor.create_dm()
            await visitor.dm_channel.send(
                f"Hello {visitor.name}, {owner} has updated their Dodo code. Use {island.code} to visit their island instead of the previous code. Remember to use '{helpMessages.COMMAND_PREFIX}leave {island.islandId}' when you're done and off their island."
            )

    elif attribute == "price":
        try:
            price = int(value)
        except ValueError:
            await ctx.send(
                "Looks like you didn't give a number for the <price> - use an integer like '500', don't type it out 'five-hundred'."
            )
            return

        oldPrice = island.price
        island.price = price

        await ctx.send(f"Price updated from {oldPrice} bells to {island.price} bells.")

    elif attribute == "size":
        try:
            size = int(value)
        except ValueError:
            await ctx.send(
                f"Looks like you didn't give a number for the queue size - use an integer like '4', don't type it out 'four'."
            )
            return

        if size < 1 or size > 7:
            await ctx.send("Please provide a valid queue size (1-7).")
            return

        oldSize = island.queueSize
        diff = size - oldSize
        island.queueSize = size

        if diff == 0:
            await ctx.send(f"{owner.name}, the queue size for you island was already {size}.")

        elif diff > 0 and island.getNumVisitors() > oldSize: #queue size got bigger, let on additional users
            for i in range(oldSize, oldSize + diff):
                if i < island.getNumVisitors():
                    await messageUser(island.visitors[i], island)

        elif diff < 0 and island.getNumVisitors() > size: #queue size got smaller, message users bumped from queue to wait
            for i in range(size, size + (diff*-1)):
                if i < island.getNumVisitors():
                    user = island.visitors[i].user
                    await user.create_dm()
                    await user.dm_channel.send(
                        f"Hello {user.name}, {island.owner.name} has updated their queue size to be smaller. If you haven't flown to their island yet, please wait until this bot messages you again. If you already are on their island, try and leave at a convienent time and then come back when this bot messages you again."
                    )

        await ctx.send(f"Queue size update from {oldSize} to {size}.")

    else:
        await ctx.send(
            f"{attribute} is not a valid attribute. Use '{helpMessages.COMMAND_PREFIX}update dodo/price/size <value>'."
        )

#--- Participating in Queue Commands ---#

#Command to add a Visitor to an Island
#Paramters: <ctx : discord.ext.commands.Context> <islandId : str> <trips : int>
@bot.command(name='join')
async def joinQueue(ctx, islandId, trips : int = 0):
    user = ctx.message.author
    island = getIslandById(islandId[-4:])

    if island == None:
        await ctx.send(f"{user.name}, {islandId} is not a valid island ID.")
        return

    if island.code == None:
        await ctx.send(f"{island.owner.name} hasn't opened the queue for their island yet.")
        return

    if DEBUG == False and island.owner == user:
        await ctx.send(f"{user.name}, you can't join the queue for your own island.")
        return

    queuePosition = island.getUserPositionInQueue(user)

    if queuePosition != -1:
        await ctx.send(
            f"{user.name}, you are already in the queue at position {queuePosition + 1} out of {island.getNumVisitors()}."
        )
        return

    island.addVisitor(user, trips)
    queuePosition = island.getUserPositionInQueue(user)

    #check if Visitor was sucessfully added
    if queuePosition == -1:
        await ctx.send(f"Failed to add {user.name} to {island.owner.name}'s queue.")
        logging.error(f"Failed to add {user} to island {island.id}.")
        return

    logging.info(f"User {user} has joined the queue for island {island.islandId} in position {queuePosition + 1}.")
    await ctx.send(
        f"{user.name}, you have been added to the queue for {island.owner.name}'s island and are currently in position {queuePosition + 1}. A DM will be sent to you from this bot with the Dodo code when it's your turn to visit the island."
    )

    #message user the dodo code if allowed on the island
    if queuePosition < island.queueSize:
        await messageUser(island.visitors[queuePosition], island)

#Command to remove a Visitor from an Island
#Parameters: <ctx : discord.ext.commands.Context> <islandId : str>
@bot.command(name='leave')
async def leaveQueue(ctx, islandId):
    user = ctx.message.author
    island = getIslandById(islandId[-4:])

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
        logging.error(f"Failed to remove {user} from island {island.islandId}.")
        return

    await ctx.send(f"Thanks {user.name}, you've been removed from the queue for {island.owner.name}'s island!")
    logging.info(f"Removed {user} from queue for island {island.islandId} from position {queuePosition + 1}. {island.getNumVisitors()} remaining in line.")

    #message next user in line the dodo code
    if queuePosition < island.queueSize and island.getNumVisitors() >= island.queueSize:
        await messageUser(island.visitors[island.queueSize-1], island)

@bot.command(name='dodo')
async def sendDodoCode(ctx, islandId):
    user = ctx.message.author
    island = getIslandById(islandId[-4:])

    if island == None:
        await ctx.send(f"{user.name}, {islandId} is not a valid island ID.")
        return

    queuePosition = island.getUserPositionInQueue(user)

    if queuePosition == -1:
        await ctx.send(f"{user.name}, you are not currently in the queue for {island.owner.name}'s island.")
        return

    if queuePosition >= island.queueSize:
        await ctx.send(
            f"{user.name}, it's not your turn to visit the island yet. Use '{helpMessages.COMMAND_PREFIX}queue {islandId}' to view the island's queue."
        )
        return

    await user.create_dm()
    await user.dm_channel.send(
        f"The Dodo code for {island.owner.name}'s island is '{island.code}'. Be sure to leave the queue with '{helpMessages.COMMAND_PREFIX}leave {island.islandId}' once you are done and completely off the island."
    )

#--- General Commands ---#

#Lists all the islands for a Server or all the users for one in a queue if an ID is provided.
#Parameters: <ctx : discord.ext.commands.Context> <islandId : str>
@bot.command(name='list')
async def listInfo(ctx, islandId : str = None):
    if islandId == None:

        if ctx.guild == None:  
            await ctx.send(f"To list all the islands for a server, call this command from a server. To list the queue for a specific island, use {helpMessages.COMMAND_PREFIX}list <island id>.")
            return

        server = getServerByGuild(ctx.guild)

        islandStr = f"Currently {len(server.islands)} open."

        if len(server.islands) > 0:
            islandStr += "\n\n```"
            for island in server.islands:
                islandStr += f"\nOwner: {island.owner.name} | ID: {island.islandId}"

                if island.price != None:
                    islandStr += f" | Bell Price: {island.price}" 

                islandStr += f" | Users in queue: {island.getNumVisitors()}"

            islandStr += f"```\n\nIsland there that isn't open? Tell the owner or an admin to use '{helpMessages.COMMAND_PREFIX}close' to close their island."
        islandStr += f"\nCreate a queue for your own island by using '{helpMessages.COMMAND_PREFIX}create'."
        await ctx.send(islandStr)

    else:

        island = getIslandById(islandId[-4:])

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

#--- Server Admin Commands ---#

@commands.has_guild_permissions(administrator=True)
@bot.command(name='channel')
async def setChannel(ctx, channel):
    channel = channel.lower()
    server = getServerByGuild(ctx.guild)

    if channel == "turnip":
        server.setTurnipChannel(ctx.channel.id, sqlConnection())
        await ctx.send(f"Turnip Channel set to {ctx.channel}.")

    elif channel == "general":
        server.setGeneralChannel(ctx.channel.id, sqlConnection())
        await ctx.send(f"General Channel set to {ctx.channel}.")

    else:
        await ctx.send(f"{channel} is not a valid channel. Use '{helpMessages.COMMAND_PREFIX}setChannel turnip/general'.")

@commands.has_guild_permissions(administrator=True)
@bot.command(name='timeout')
async def setTimeout(ctx, time : int):
    server = getServerByGuild(ctx.guild)

    oldTimeout = server.timeout

    server.setTimeout(time, sqlConnection())

    await ctx.send(f"User timeout updated from {oldTimeout} to {server.timeout} minutes.")

#--- Bot Owner Commands ---#

@commands.is_owner()
@bot.command(name='servers')
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
        await ctx.send(f"Looks like you're missing an argument - use '{helpMessages.COMMAND_PREFIX}remove <position> <islandId (Optional)>'")
    else:
        raise

@updateQueue.error
async def updateError(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Looks like you're missing an argument - Use '{helpMessages.COMMAND_PREFIX}update dodo/price/size <value>'.")
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

@setChannel.error
async def setChannelError(ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send("This command can't be called in a DM.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have admin permissions on this server.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Looks like you're missing an argument - use '{helpMessages.COMMAND_PREFIX}setChannel turnip/general'.")
    else:
        raise

@setTimeout.error
async def setTimeoutError(ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send("This command can't be called in a DM.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have admin permissions on this server.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Looks like you're missing an argument - use '{helpMessages.COMMAND_PREFIX}setTimeout <time>'.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Looks like you didn't give a number for the time - use an integer like '20', don't type it out.")
    else:
        raise

@listServers.error
async def listServersError(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("Only the owner of the bot can call this command.")
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

    elif com == "open":
        helpStr = helpMessages.OPEN

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

    elif com == "list":
        helpStr = helpMessages.LIST

    elif com == "channel":
        helpStr = helpMessages.CHANNEL

    elif com == "timeout":
        helpStr = helpMessages.TIMEOUT

    else:
        helpStr = f"{com} is not a valid command. Use '{helpMessages.COMMAND_PREFIX}help' to list this bot's available commands."

    await ctx.send(helpStr)

bot.loop.create_task(clean())
bot.run(TOKEN)