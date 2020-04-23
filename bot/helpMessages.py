"""
Animal Crossing New Horizons Island Queue Discord Bot
Author: Marshall Jankovsky
github.com/marshalltj/island-queue-bot

Version: 1.0.0

helpMessages.py contains strings used for the !help command to keep bot.py cleaner. It also is where the COMMAND_PREFIX can be changed.
"""

COMMAND_PREFIX="!"

MENU="```Island Queue Bot" + \
"\nCommands for Managing a Queue:" + \
"\n  create    Create a queue for your island (DM only command)" + \
"\n  close     Close your island queue" + \
"\n  remove    Remove someone from a position in your island queue" + \
"\nCommands for Participating in a Queue:" + \
"\n  join      Join an island queue" + \
"\n  leave     Leave an island queue" + \
"\nGeneral Commands:" + \
"\n  islands   List all currently open islands" + \
"\n  queue     List all users in a queue for an island" + \
f"\n\nUse {COMMAND_PREFIX}help <command> for more info on a command." + \
"```"

CREATE="```Creating an Island Queue:" + \
f"\n\nUsage: {COMMAND_PREFIX}create <dodo code> <turnip price (Optional)> <queue size (Optional)>" + \
"\n\nRestrictions: A user can only have one island queue. This command must be DM'd to the bot (to hide the Dodo code from other users)." + \
"\n\nCreates a queue that users can join to visit your island. Upon successful creation, a unique Island ID is created for your island and a message will be sent to a pre-defined channel telling users they can join the queue. This bot defaults to allow three users on an island at a time (<queue size>)." + \
f"\n\nIf you want to provide a <queue size> but not <turnip price>, simply enter a valid queue size as the second arguement (1-7). IE: '{COMMAND_PREFIX}create DODO 5' will create a queue that allows 5 concurrent users on your island at a time." + \
"```" 

CLOSE="```Closing an Island Queue:" + \
f"\n\nUsage: {COMMAND_PREFIX}close" + \
"\n\nCloses the queue to your island, even if there are still users in the queue. A message will be sent to a pre-defined channel telling users the queue has closed as well as listing and listing any users that were still in the queue." + \
"```"

REMOVE="```Removing a User from your Queue:" + \
f"\n\nUsage: {COMMAND_PREFIX}remove <queue position>" + \
f"\n\nRemoves a user from <queue position> in your island queue. Upon removal, a DM is sent to the removed user and the queue is updated, letting in any new users if applicable. Useful if a user forgets to use the {COMMAND_PREFIX}leave command when they're done visiting your island." + \
"```"

JOIN="```Joining an Island Queue:" + \
f"\n\nUsage: {COMMAND_PREFIX}join <island ID>" + \
f"\n\nJoin the queue for visiting an island. Once it's your turn to visit the island, the bot will DM you a message with a Dodo code for the island. Using {COMMAND_PREFIX}join when already in a queue will list your position in that queue." + \
"```"

LEAVE="```Leaving an Island Queue:" + \
f"\n\nUsage: {COMMAND_PREFIX}leave <island ID>" + \
"\n\nRemove yourself from the queue for visiting an island once you're done. Upon removal, the queue is updated, letting in any new users to the island if applicable." + \
"```"

ISLANDS="```Listing open Islands:" + \
f"\n\nUsage: {COMMAND_PREFIX}islands" + \
"\n\nPrints all open islands, their owners, bell price, and number of users in the queue." + \
"```"

QUEUE="```Viewing an Island's Queue:" + \
f"\n\nUsage: {COMMAND_PREFIX}queue <island ID>" + \
"\n\nPrints information about the island in a header then lists the current users in the queue. Users that are currently allowed on the island will be framed with formatting." + \
"```"