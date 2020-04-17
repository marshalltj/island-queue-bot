# Animal Crossing Island Queue Manager Discord Bot
This is a discord bot built for managing queues to visit another player's island. I ended up making this for a medium-sized discord server I'm a part of where we share our turnip prices and buy/sell on each other's islands. With about 15-20 active contributors, we ended up having quite a waitlist to visit each other's island to sell our turnips.

We tried using [turnip.exchange](turnip.exchange) to manage this but ran into persistency problems with having to keep open tabs with the website running. This bot does basically the same thing but does it through commands on a discord server so you don't need to have a computer open.

# Commands
This bot prefixes all commands with '!', but this can be easily changed in [helpMessages.py](bot/helpMessages.py).

- [Managing an Island Queue](#managing-an-island-queue)
  - [Create](#create)
  - [Close](#close)
  - [Remove](#remove)
- [Participating in an Island Queue](#participating-in-an-island-queue)
  - [Join](#join)
  - [Leave](#leave)
- [General Commands](#general-commands)
  - [Island](#island)
  - [Queue](#queue)
  - [Help](#help)

## Managing an Island Queue

### Create
>**Usage**: `!create <dodo code> <bell price (Optional)> <queue size (Optional)>`
>
>**Arguments**:
>- `<dodo code>`: The dodo code for the island.
>- `<bell price>`: Used to determine if it should alert users in the `TURNIP_CHANNEL` that an island has been opened.
>- `<queue_size>`: Used to set the number of concurrent users allowed on an island at a time. Valid values are 1-7. Defaults to 3.
>
>**Restrictions**:
>- A user can only have one queue open at a time.
>- This command can only be issued through a DM, though the bot will print an error message if a user tries to execute it in a channel.
>
>**Description**:
>
>Creates a queue for a user's island and broadcasts a message to the `GENERAL_CHANNEL` and whatever channel the command was executed from that a queue has been created with instructions on how to join. A unique 3-digit ID is assigned to it that will be used to identify it to users when executing commands like `!join` or `!queue`.
>
>If `<bell price>` is provided, the bot will look at the current day to determine if it's a sell or buy day and message the `TURNIP_CHANNEL` instead of the `GENERAL_CHANNEL`.
>
>If you want to provide a `<queue size>` but no `<bell price>`, as long as your `<queue size>` is valid (1-7) simply enter it as the second argument - IE: `!create DODO 5`.

### Close
>**Usage**: `!close`
>
>**Restrictions**:
>- A user can only close an island queue they own.
>
>**Description**:
>
>Closes the user's open island queue if they have one. A message will be broadcasted to the `GENERAL_CHANNEL` (or `TURNIP_CHANNEL` if a `<bell price>` was provided when created) and whatever channel the command was executed from that the island queue has closed. If there were any users left in the queue their usernames are also listed in the order that they were in the queue.

### Remove
>**Usage**: `!remove <position>`
>
>**Arguments**:
>- `<position>`: The position in the queue of the user to be removed.
>
>**Restrictions**:
>- A user can only remove other users from an island queue they own.
>
>**Description**:
>
>Removes a user from an island queue that the user who called the command owns. Upon removal, a DM is sent to the removed user informing them that they were removed. Sends the next user in line the `<dodo code>` via DM if the removed user was allowed on the island.

## Participating in an Island Queue

### Join
>**Usage**: `!join <island id>`
>
>**Arguments**:
>- `<island id>`: The unique ID of the island queue to join.
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
>**Usage**: `!leave <island id>`
>
>**Arguments**:
>- `<island id>`: The unique ID of the island queue to leave.
>
>**Description**:
>
>Removes the user from an island queue they've joined. If the user leaves and this action makes room on the island to allow another user, a DM will be sent to the next user in line that contains the island's `<dodo code>`.

## General Commands

### Islands
>**Usage**: `!islands`
>
>**Description**:
>
>Prints a list of all open island queues along with their owner, bell price (if applicable), and number of current users in the queue.

### Queue
>**Usage**: `!queue <island id>`
>
>**Arguments**:
>- `<island id>`: The unique ID of the island queue to display.
>
>**Description**:
>
>Prints the users in an island queue along with the owner, bell price (if applicable), and number of current users in the queue. Users currently allowed on the island will be demarcated with a frame around them.

### Help
>**Usage**: `!help <command (Optional)>`
>
>**Arguments**:
>- `<command>` - The command to display help documents on.
>
>**Description**:
>
>Prints a list of available commands and a brief description. If `<command>` if provided, prints more in-depth descriptions on what the command does.
