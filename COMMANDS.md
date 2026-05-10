# Command Reference

This file lists every slash command in the Discord bot and explains its purpose.

## Moderation Commands

| Command | Purpose |
| --- | --- |
| `/kick` | Kicks a member from the server and logs the action. |
| `/ban` | Bans a member from the server, optionally deleting recent messages, and logs the action. |
| `/unban` | Unbans a user by Discord user ID and logs the action. |
| `/mute` | Temporarily mutes a member using Discord timeout and optionally applies the configured muted role. |
| `/unmute` | Removes a member timeout and removes the configured muted role if present. |
| `/warn` | Sends a warning to a member and records the warning in the log channel. |
| `/clear` | Deletes a selected number of recent messages from the current channel. |

## Role Commands

| Command | Purpose |
| --- | --- |
| `/addrole` | Adds a selected role to a member. |
| `/removerole` | Removes a selected role from a member. |
| `/secretrole` | Gives the configured private role when the correct secret password is entered. |
| `/reactionrole add` | Connects an emoji reaction on a message to a role. |
| `/reactionrole remove` | Removes an existing reaction-role mapping. |
| `/reactionrole list` | Shows configured reaction-role mappings. |

## Interaction Commands

| Command | Purpose |
| --- | --- |
| `/hello` | Sends a friendly greeting. |
| `/ping` | Shows the bot latency in milliseconds. |
| `/say` | Sends a message through the bot, usually used by moderators. |
| `/8ball` | Answers a question with a random magic 8-ball response. |
| `/dm` | Sends a direct message to a member from the server staff. |

## Ticket Commands

| Command | Purpose |
| --- | --- |
| `/ticket` | Creates a private ticket channel for a user and staff. |
| `/close` | Closes and deletes the current ticket channel. |

## Poll Commands

| Command | Purpose |
| --- | --- |
| `/poll` | Creates a poll with emoji reactions. If no options are provided, it creates a yes/no poll. |

## Welcome System

The welcome and goodbye system does not use slash commands. It works automatically through Discord member events.

| Event | Purpose |
| --- | --- |
| Member joins | Sends a welcome message to the configured welcome channel. |
| Member leaves | Sends a goodbye message to the configured goodbye channel. |

## Information Commands

| Command | Purpose |
| --- | --- |
| `/serverinfo` | Shows server information such as owner, member count, role count, channel count, and creation date. |
| `/userinfo` | Shows information about a selected member or the command user. |
| `/botinfo` | Shows information about the bot, including latency, Python version, and discord.py version. |

## Utility Commands

| Command | Purpose |
| --- | --- |
| `/coinflip` | Randomly returns heads or tails. |
| `/dice` | Rolls one or more dice with a selected number of sides. |
| `/randomnumber` | Generates a random number inside a selected range. |

## Permission Notes

- Moderator commands require Discord permissions or the configured moderator role.
- Role commands require the bot to have **Manage Roles**.
- Ticket commands require the bot to have **Manage Channels**.
- Poll and reaction-role commands require the bot to have **Add Reactions**.
- The bot role must be higher than any role it needs to manage.
