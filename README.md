# Animal Crossing Island Queue Manager Discord Bot
Dropping a Dodo code in a discord full of bell-hungry turnip traders is a surefire way to have everyone involved be stuck in loading screens. This Discord bot was made to help ease the pain of letting a long line of players on to your island.

An island owner can send a direct-message the bot with their Dodo Code to create a queue. The bot creates a unique ID that other users can use to join a queue to get messaged the Dodo Code when it's their turn to join. Once finished, the user leaves the queue using a command and the next user in line gets the Dodo Code messaged to them.

Island owners can choose the number of users they want to let in at a given time (the bot defaults to three) as well as provide a Turnip price to let users know what their buy/sell prices are.

**Table of Contents**
- [Commands](#commands)
- [Installing the Bot](#installing-the-bot)
  - [Create your Bot on Discord](#create-your-bot-on-discord)
  - [Add the Bot to your Server](#add-the-bot-to-your-server)
  - [Running the Bot Locally](#running-the-bot-locally)
  - [Hosting the Bot on Heroku](#hosting-the-bot-on-heroku)

# Commands
This bot prefixes all commands with '!', but this can be easily changed in [helpMessages.py](bot/helpMessages.py).

**Commands Quicklinks**
- [Managing an Island Queue](#managing-an-island-queue)
  - [Create](#create)
  - [Close](#close)
  - [Remove](#remove)
- [Participating in an Island Queue](#participating-in-an-island-queue)
  - [Join](#join)
  - [Leave](#leave)
  - [Dodo](#remove)
- [General Commands](#general-commands)
  - [Island](#island)
  - [Queue](#queue)
  - [Help](#help)

## Managing an Island Queue

### Create
>**Usage**: `!create <dodo code> <bell price (Optional)> <queue size (Optional)>`
>
>**Example**: `!create Q05ZA 550 4`
>>Creates a queue for your island that users can visit with `<dodo code>` Q05ZA, lets users know your `<bell price>` is 550 and a `<queue size>` that allows 4 users on at a time.
>
>**Arguments**:
>- `<dodo code>`: The dodo code for the island.
>- `<bell price>`: Used to determine if it should alert users in the `TURNIP_CHANNEL` that an island has been opened.
>- `<queue_size>`: Used to set the number of concurrent users allowed on an island at a time. Valid values are 1-7. Defaults to 3.
>
>**Restrictions**:
>- An island owner can only have one queue open at a time.
>- This command can only be issued through a DM, though the bot will print an error message if an island owner tries to execute it in a channel.
>
>**Description**:
>
>Creates a queue for an island owner and broadcasts a message to the `GENERAL_CHANNEL` and whatever channel the command was executed from that a queue has been created with instructions on how to join. A unique 3-digit ID is assigned to it that will be used to identify it to users when executing commands like `!join` or `!queue`.
>
>If `<bell price>` is provided, the bot will look at the current day to determine if it's a sell or buy day and message the `TURNIP_CHANNEL` instead of the `GENERAL_CHANNEL`.
>
>If you want to provide a `<queue size>` but no `<bell price>`, as long as your `<queue size>` is valid (1-7) simply enter it as the second argument - IE: `!create DODO 5`.

### Close
>**Usage**: `!close <island id (Optional/Admin Only)>`
>
>**Arguments**:
>- `<island id>`: The unique ID of the island to close (server admin only).
>
>**Restrictions**:
>- An island owner can only close an island queue they own.
>
>**Description**:
>
>Closes the island owner's open queue if they have one. If an `<island id>` is provided and the user sending the command is an admin, closes the specified island. A message will be broadcasted to the `GENERAL_CHANNEL` (or `TURNIP_CHANNEL` if a `<bell price>` was provided when created) and whatever channel the command was executed from that the island queue has closed. If there were any users left in the queue their usernames are also listed in the order that they were in the queue.

### Remove
>**Usage**: `!remove <position> <island id (Optional/Admin Only)>`
>
>**Example**: `!remove 2`
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
>Removes a user from an island queue that the an island owner owns. If an `<island id>` is provided and the user sending the command is an admin, removes a user from the specified island. Upon removal, a DM is sent to the removed user informing them that they were removed. Sends the next user in line the `<dodo code>` via DM if the removed user was allowed on the island at the time of their removal.

## Participating in an Island Queue

### Join
>**Usage**: `!join <island id> <number of trips (Optional)>`
>
>**Example**: `!join 327 2`
>> Joins the queue for an island with a unique `<island id>` of 327 and lets other users know you plan on taking 2 trips (`<number of trips>`).
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
>**Example**: `!leave 327`
>> Removes you from the queue for an island with a unique `<island id>` of 327.
>
>**Arguments**:
>- `<island id>`: The unique ID of the island queue to leave.
>
>**Description**:
>
>Removes the user from an island queue they've joined. If the user leaves and this action makes room on the island to allow another user, a DM will be sent to the next user in line that contains the island's `<dodo code>`.

### Dodo
>**Usage**: `!dodo <island id>`
>
>**Example**: `!dodo 327`
>> Has the bot message you the dodo code for an island with a unique `<island id>` of 327 if it's your turn to visit the island.
>
>**Arguments**:
>- `<island id>`: The unique ID of the island queue to get the dodo code for.
>
>**Description**:
>
>Messages the user with the dodo code for an island if it's their turn to visit. Useful if there are any issues with messaging or if the user previously didn't allow messages from bots.

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
>**Example**: `!queue 327`
>> Displays information about and all users currently in the queue for an island with a unique `<island id>` of 327.
>
>**Arguments**:
>- `<island id>`: The unique ID of the island queue to display.
>
>**Description**:
>
>Prints the users in an island queue along with the owner, bell price (if applicable), and number of current users in the queue along with the number of trips they plan on taking. Users currently allowed on the island will be demarcated with a frame around them and their time spent being allowed on the island in minutes will be shown next to their name.

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

# Installing the Bot
This bot is coded to manage a single server, so you will need to install it yourself to use it.

## Create your Bot on Discord
- Go to [the Discord Developer Portal](https://discordapp.com/developers/applications) and create a new application.
- Navigate to the "Bot" tab in your application
- Press the "Add Bot" button.

## Add the Bot to your Server
- In your bot application, navigate to the "OAuth2" tab.
- In the "Scopes" table, select "bot".
- In the "Permissions" table, select "View Channels" and "Send Messages".
- Copy the link at the bottom of the "Scopes" table and open it.
- Follow the prompts to add the bot to a server you manage.

## Running the Bot Locally
- Clone this repository locally and navigate to the [bot](bot/) folder in your command line.
- Fill in the values in your [.env](bot/.env) file - these values should be directly pasted after the `=` with no additional characters.
   - `DISCORD_TOKEN` is your bot's token.
      > You can get your bot's token from the [the Discord Developer Portal](https://discordapp.com/developers/applications) by opening your bot application, navigating to the "Bot" tab and copying the "Token". **DO NOT** share this token or post it anywhere publicly.

   - `TURNIP_CHANNEL` is the channel ID the bot will post messages about island queues that were created with a `<bell price>` included.
      >You can get the ID for a Discord channel by changing your settings to developer mode in User Settings -> Appearance -> Enable Developer Mode

   - `GENERAL_CHANNEL` is the channel ID the bot will post messages about island queues that did not include a `<bell price>`.
      >If you want the bot to only post to one channel, simply set both `TURNIP_CHANNEL` and `GENERAL_CHANNEL` to the same ID. You can also leave these fields blank but it's not advised.

- Install discord.py and dotenv with [pip](https://realpython.com/what-is-pip/):

      pip install -U discord.py
      pip install -U python-dotenv

- Run the bot (requires Python 3.6 or greater):

      python bot.py

You should now see the bot come online on your server! Note that this is just locally running the bot, so if you close your command line or computer the bot will go offline. I recommend hosting the bot on a cloud server - see the next section for insturctions on how to do that.

## Hosting the Bot on [Heroku](https://id.heroku.com/login)
There are many different hosting options, I was able to host my instance of the bot just fine using [Heroku](https://id.heroku.com/login) and the setup is pretty easy. I've also provided files to interface with Herou's pipeline in the [herokuPipelineFiles](herokuPipelineFiles/) directory. Follow the instructions in the [Running the Bot Locally](#running-the-bot-locally) and then continue here.

### Setting up the Bot Application on Heroku
- Create an account on [Heroku](https://id.heroku.com/login).
- Create a new app called "island-queue-bot".
- Navigate to your application settings and press the "Add buildpack" button.
- Select the Python buildpack and Save changes.

### Setting up the Heroku Git Repository
- Download and install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-command-line).

- Create a new directory outside of the cloned island-queue-bot BitBucket repository and run the following commands:

      heroku login
      heroku git:clone -a island-queue-bot

  > If you named your application on heroku something else use that instead of `island-queue-bot`.

- Navigate back to the BitBucket repository and copy everything from your [bot](/bot) and [herokuPipelineFiles](/herokuPipelineFiles) to the new Heroku Git repository.

- Add and commit all the files (don't forget .env) and push using:

      git push heroku master

### Running the Bot on Heroku
Once it's finished installing on the command line, go back to your application on the Heroku website and go to the "Resources" tab for your app. You'll see a slider with a price to the right of it and a pencil icon. Click the pencil icon then turn the slider on to start running your bot.
