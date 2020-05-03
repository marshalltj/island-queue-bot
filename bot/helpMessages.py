"""
Animal Crossing New Horizons Island Queue Discord Bot
Author: Marshall Jankovsky
github.com/marshalltj/island-queue-bot

Version: 2.0.0

helpMessages.py contains strings used for the !help command to keep bot.py cleaner. It also is where the COMMAND_PREFIX can be changed.
"""

COMMAND_PREFIX="!island "

MENU="```Island Queue Bot" + \
"\nCommands for Managing a Queue:" + \
"\n  create    Create an ID for your island" + \
"\n  open      Open your island queue" + \
"\n  close     Close your island queue" + \
"\n  remove    Remove someone from a position in your queue" + \
"\n  update    Change your island's properties" + \
"\nCommands for Participating in a Queue:" + \
"\n  join      Join an island queue" + \
"\n  leave     Leave an island queue" + \
"\n  dodo      Get the Dodo code for an island resent to you" + \
"\nGeneral Commands:" + \
"\n  list      List info about an island or all islands" + \
"\nCommands for Server Admins:" + \
"\n  channel   Set the channels the bot broadcasts msgs to" + \
"\n  timeout   Set the time a user is allowed on an island" + \
f"\n\nUse {COMMAND_PREFIX}help <command> for more info on a command.\n\nVisit github.com/marshalltj/island-queue-bot for additional documentaion." + \
"```"

CREATE="```Creating an Island:" + \
f"\n\nUsage: {COMMAND_PREFIX}create <turnip price (Optional)>" + \
"\n\nRestrictions: A user can only have one island created." + \
f"\n\nCreates a unique ID for you island that users can use to join and visit your island. Users can't join until the {COMMAND_PREFIX}open command has been called for the island." + \
"```" 

OPEN="```Opening an Island Queue:" + \
f"\n\nUsage: {COMMAND_PREFIX}open <dodo code> <queue size (Optional>" + \
"\n\nRestrictions: This command must be sent to the bot via DM (to hide Dodo code)." + \
"\n\nOpens the queue to your island so that users can join it. The <queue size> is how many users are allowed on at once (default 3)." + \
"```"

CLOSE="```Closing an Island Queue:" + \
f"\n\nUsage: {COMMAND_PREFIX}close <island ID (Optional)>" + \
"\n\nCloses the queue to your island, even if there are still users in the queue. If an island ID is provided and the user calling the command is an admin to the server associated with the island, it will close the specified island. A message will be sent to a pre-defined channel telling users the queue has closed as well as listing and listing any users that were still in the queue." + \
"```"

REMOVE="```Removing a User from your Queue:" + \
f"\n\nUsage: {COMMAND_PREFIX}remove <queue position> <island ID (Optional)>" + \
f"\n\nRemoves a user from <queue position> in your island queue. If <island ID> is provided and you are a server admin you can remove a user from a queue you don't own. Upon removal, a DM is sent to the removed user and the queue is updated, letting in any new users if applicable. Useful if a user forgets to use the {COMMAND_PREFIX}leave command when they're done visiting your island." + \
"```"

UPDATE="```Updating an Island:" + \
f"\n\nUsage: {COMMAND_PREFIX}update <'dodo'/'price'/'size'> <updated value>" + \
"\n\nUpdates the specified property to the <updated value>. If <dodo> is provided, users that are allowed on will be messaged the new code. If the <size> (queue size) is changed, users will be messaged that are affected by the change." + \
"```"

JOIN="```Joining an Island Queue:" + \
f"\n\nUsage: {COMMAND_PREFIX}join <island ID> <number of trips (Optional)>" + \
f"\n\nJoin the queue for visiting an island. Once it's your turn to visit the island, the bot will DM you a message with a Dodo code for the island. Using {COMMAND_PREFIX}join when already in a queue will list your position in that queue." + \
"```"

LEAVE="```Leaving an Island Queue:" + \
f"\n\nUsage: {COMMAND_PREFIX}leave <island ID>" + \
"\n\nRemove yourself from the queue for visiting an island once you're done. Upon removal, the queue is updated, letting in any new users to the island if applicable." + \
"```"

DODO="```Getting the Island's Dodo Code:" + \
f"\n\nUsage: {COMMAND_PREFIX}dodo <island ID>" + \
"\n\nHave the bot resend the Dodo code for the island queue you're in if it's your turn to visit the island." + \
"```"

LIST="```Listing Information about Islands:" + \
f"\n\nUsage: {COMMAND_PREFIX}islands <island id (Optional)>" + \
"\n\nPrints all open islands, their owners, bell price, and number of users in the queue. If an <island id> is provided, prints information about the island in a header then lists the current users in the queue and how many trips they plan to take. Users that are currently allowed on the island will be framed with formatting along with the amount of time they've been allowed on the island." + \
"```"

CHANNEL="```Setting Broadcast Channels:" + \
f"\n\nUsage: {COMMAND_PREFIX}channel <'turnip'/'general'>" + \
"\n\nRestrictions: Only server admins can user this command." + \
"\n\nSets the <turnip> or <general> channel to whatever channel this command was called in. The bot will broadcast information about open Island queues to these channels. These don't have to be set but it's recommended to set them (they can be the same)." + \
"```"

TIMEOUT="```Seting the User Timeout:" + \
f"\n\nUsage: {COMMAND_PREFIX}timeout <minutes>" + \
"\n\nRestrictions: Only server admins can user this command." + \
"\n\nSets the amount of time users are allowed on an island before they are automatically removed from the queue. Deafulted to 30 minutes. Users are removed every 5 minutes so it can be up to 5 minutes passed <minutes> until they are actually removed." + \
"```"