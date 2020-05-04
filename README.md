# Animal Crossing Island Queue Manager Discord Bot
### Version 2.0.0
Dropping a Dodo code in a discord full of bell-hungry turnip traders is a surefire way to have everyone involved be stuck in loading screens. This Discord bot was made to help ease the pain of letting a long line of players on to your island.

An island owner can send a direct-message the bot with their Dodo Code to create a queue. The bot creates a unique ID that other users can use to join a queue to get messaged the Dodo Code when it's their turn to join. Once finished, the user leaves the queue using a command and the next user in line gets the Dodo Code messaged to them.

Island owners can choose the number of users they want to let in at a given time (the bot defaults to three) as well as provide a Turnip price to let users know what their buy/sell prices are.

# Adding the Bot to your Server
To add the bot to your server, simply use [this link](https://discordapp.com/api/oauth2/authorize?client_id=700478877419438152&permissions=3072&scope=bot) and follow the prompts. A custom role will be created for the bot to allow it permissions to view channels and messages and send messages.

There are two things that should be configured once added:
- The channel the bot will send messages about queues with turnip prices.
- The channel the bot will send messages about queues without turnip prices.

A server admin can use the [`!island channel`](#channel) to set these. These can both be set to the same channel if desired, and these can be changed at any time.

Users are by default allowed on an island queue for 30 minutes before they are automatically removed, server admins can modify this value with [`!island timeout`](#timeout).

# Commands
This bot prefixes all commands with '!island'.

**Commands Quicklinks**
- [Managing an Island Queue](#managing-an-island-queue)
  - [Create](#create)
  - [Open](#open)
  - [Close](#close)
  - [Remove](#remove)
  - [Update](#update)
- [Participating in an Island Queue](#participating-in-an-island-queue)
  - [Join](#join)
  - [Leave](#leave)
  - [Dodo](#remove)
- [General Commands](#general-commands)
  - [List](#list)
  - [Help](#help)
- [Server Admin Commands](#server-admin-commands)
  - [Channel](#channel)
  - [Timeout](#timeout)

## Managing an Island Queue

### Create
>**Usage**: `!island create <bell price (Optional)>`
>
>**Example**: `!island create 550`
>>Creates an ID for your island that users can visit once it's opened and lets users know your `<bell price>` is 550.
>
>**Arguments**:
>- `<bell price>`: Used to determine if it should alert users in the turnipChannel that an island has been opened.
>
>**Restrictions**:
>- An island owner can only have own one island.
>- This command can't be sent in a DM.
>
>**Description**:
>
>Creates an island object for the owner. A unique 4-digit ID is assigned to it that will be used to identify it to users when executing commands like `!island join` or `!island queue` once the queue for the island is opened using `!island open`.
>
>If `<bell price>` is provided, the bot will message the server's turnipChannel instead of the generalChannel once the island is open.

### Open
>**Usage**: `!island open <dodo code> <queue size (Optional)>`
>
>**Example**: `island open QZ04P 5`
>>Creates a queue for the owner's island that users can visit with `<dodo code>` QZ04P and a `<queue size>` that allows 5 users on at once.
>
>**Arguments**:
>- `<dodo code>`: The Dodo code user's can use to visit the island.
>- `<queue size>`: The number of users allowed on an island at a time (default 3).
>
>**Restrictions**:
>- This command must be sent to the bot in a Direct Message.
>
>**Description**:
>
>Opens an island queue to allow users to join it and visit the owner's island. Upon successful opening, a message is broadcast to the server's configured channels. If no `<queue size>` is provided a default of 3 is set.

### Close
>**Usage**: `!island close <island id (Optional/Admin Only)>`
>
>**Arguments**:
>- `<island id>`: The unique ID of the island to close (server admin only).
>
>**Restrictions**:
>- An island owner can only close an island queue they own. Server admins can close islands opened on their server.
>
>**Description**:
>
>Closes the island owner's open queue if they have one. If an `<island id>` is provided and the user sending the command is an admin, this command closes the specified island. A message will be broadcasted to the server's generalChannel (or turnipChannel if a `<bell price>` was provided when created) and whatever channel the command was executed from that the island queue has closed. If there were any users left in the queue their usernames are also listed in the order that they were in the queue.

### Remove
>**Usage**: `!island remove <position> <island id (Optional/Admin Only)>`
>
>**Example**: `!island remove 2`
>> Removes the second user in line (`<position>`) from your island queue.
>
>**Arguments**:
>- `<position>`: The position in the queue of the user to be removed.
>- `<island id>`: The unique ID of the island to remove a user from (server admin only).
>
>**Restrictions**:
>- An island owner can only remove users from an island queue they own. Server admins can remove a user from any open island.
>
>**Description**:
>
>Removes a user from an island queue that the an island owner owns. If an `<island id>` is provided and the user sending the command is an admin, this command removes a user from the specified island. Upon removal, a DM is sent to the removed user informing them that they were removed. Sends the next user in line the `<dodo code>` via DM if the removed user was allowed on the island at the time of their removal.

### Update
>**Usage**: `!island update <"dodo"/"size"/"price"> <updated value>`
>
>**Examples**:
>
> `!island update dodo ZP5K7`
>> Updates the Dodo code for the user's island to ZP5K7.
>
> `!island update size 5`
>> Updates the queue size for the user's island to 5.
>
>**Arguments**:
>- `<"dodo"/"size"/"price">`: Which property to update.
>- `<updated value>`: The value of the updated property.
>
>**Restrictions**:
>- If `<dodo>` is the property to update, this command can only be issued through a DM.
>
>**Description**:
>
>Updates various properties for and island. If the property is `<dodo>`, all users that are currently allowed on the island will be messaged the new dodo code. If the queue size (`<size>`) is updated to be smaller, users who were previously allowed on will be messaged to be asked to leave the island until the bot messages them again. If the size is larger the bot will message any new users that are now allowed on.

## Participating in an Island Queue

### Join
>**Usage**: `!island join <island id> <number of trips (Optional)>`
>
>**Example**: `!island join 3271 2`
>> Joins the queue for an island with a unique `<island id>` of 3271 and lets other users know you plan on taking 2 trips (`<number of trips>`).
>
>**Arguments**:
>- `<island id>`: The unique ID of the island queue to join.
>- `<number of trips>`: The number of trips the user plans to make to the island.
>
>**Restrictions**:
>- A user can only join an island queue if they are not already in it.
>
>**Description**:
>
>Adds the user to the back of the queue for an island. If the user joins and there is room on the island to allow another user, a DM will be sent to the user that contains the island's `<dodo code>`.
>
>If the user is already in the island queue, a message will be printed that states their position in the queue.

### Leave
>**Usage**: `!island leave <island id>`
>
>**Example**: `!island leave 3271`
>> Removes you from the queue for an island with a unique `<island id>` of 3271.
>
>**Arguments**:
>- `<island id>`: The unique ID of the island queue to leave.
>
>**Description**:
>
>Removes the user from an island queue they've joined. If the user leaves and this action makes room on the island to allow another user, a DM will be sent to the next user in line that contains the island's `<dodo code>`.

### Dodo
>**Usage**: `!island dodo <island id>`
>
>**Example**: `!island dodo 3271`
>> Has the bot message you the dodo code for an island with a unique `<island id>` of 3271 if it's your turn to visit the island.
>
>**Arguments**:
>- `<island id>`: The unique ID of the island queue to get the dodo code for.
>
>**Description**:
>
>Messages the user with the dodo code for an island if it's their turn to visit. Useful if there are any issues with messaging or if the user previously didn't allow messages from the bot.

## General Commands

### List
>**Usage**: `!island list <island id (Optional)>`
>
>**Examples**:
>
>`!island list`
>> List all the open islands on the server the command is called from.
>
>`!island list 3721`
>> Lists the users in the queue for an island with an `<island id>` of 3721.
>
>**Arguments**:
>- `<island id>`: The unique ID of the island queue to display.
>
>**Restrictions**:
>- If no `<island id>` is provided, this command must be called in a server.
>
>**Description**:
>
>Prints a list of all open island queues along with their owner, bell price (if applicable), and number of current users in the queue in a server. If an `<island id>` is provided, it lists all the users in the queue. Users allowed on will have their time spent displayed.

### Help
>**Usage**: `!help <command (Optional)>`
>
>**Example**: `!help create`
>> Displays the help docs for the create `<command>`.
>
>**Arguments**:
>- `<command>` - The command to display help documents on.
>
>**Description**:
>
>Prints a list of available commands and a brief description. If `<command>` if provided, prints more in-depth descriptions on what the command does.

## Server Admin Commands

### Channel
>**Usage**: `!island channel <"turnip"/"general">`
>
>**Example**: `!island channel turnip`
>> Sets the turnip queue broadcast channel to the channel this was called from.
>
>**Arguments**:
>- `<"turnip"/"general">` - Which broadcast channel to update.
>
>**Restrictions**:
>- Only server admins can use the command.
>- This command can't be sent in a DM.
>
>**Description**:
>
>Sets the broadcast channels for a server. These channels are used when island queue is opened or closed. While these channels don't have to be set it is recommended that they are. The generalChannel and turnipChannel can be the same.

### Timeout
>**Usage**: `!island timeout <minutes>`
>
>**Example**: `!island timeout 45`
>> Sets the timeout period for users to be allowed on an island to 45 minutes.
>
>**Arguments**:
>- `<minutes>` - The number of minutes a user is allowed on an island.
>
>**Restrictions**:
>- Only server admins can use the command.
>- This command can't be sent in a DM.
>
>**Description**:
>
>Sets the amount of time a user is allowed to be on an island. Every 5 minutes the bot cleans users who have spent too much time on an island and automatically removes them from island queues. This property is by default set to 30 for each server.
