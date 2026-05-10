# Project Report: Discord.py Community Bot

## Introduction

This project is a Discord server management bot developed in Python using the `discord.py` library. The bot helps server administrators manage moderation, roles, tickets, polls, welcome messages, and general utility commands through Discord slash commands.

The project follows a modular cog-based structure, which separates features into different files. This makes the bot easier to understand, maintain, test, and expand.

## Objectives

- Build a working Discord bot using Python.
- Use slash commands for a modern Discord user experience.
- Provide useful moderation commands for server staff.
- Add automated bad-word filtering with logging.
- Create a role management system including reaction roles and a secret role.
- Provide a private ticket system for user support.
- Add fun and utility commands for general server interaction.
- Store configurable values in `config.json` instead of hardcoding them.
- Store the bot token securely in a `.env` file.
- Organize code into cogs and utility modules.

## Features

### Moderation

The bot supports kick, ban, unban, mute, unmute, warn, and clear messages. These commands use permission checks so only authorized staff members can use them.

### Bad-Word Filter

The bot checks messages against the configured bad-word list. If a blocked word is found, the message is deleted, the user is warned in the channel, and the action is logged.

### Role Management

The bot can add and remove roles from members. It also includes a secret role command that gives a private role only when the correct password is entered.

### Reaction Roles

Moderators can connect a message reaction to a role. When a user reacts with the configured emoji, the bot gives the role. When the reaction is removed, the role is removed.

### Interaction Commands

The bot includes simple commands like hello, ping, say, 8-ball, and DM. These commands improve server interaction and allow staff to communicate through the bot.

### Ticket System

Users can open private support tickets. The bot creates a private channel visible only to the user, staff, and the bot. The ticket can be closed with the close command.

### Poll System

The poll command creates polls using emoji reactions. It supports yes/no polls and multiple-choice polls.

### Welcome and Goodbye Messages

The bot automatically sends welcome messages when members join and goodbye messages when members leave.

### Information Commands

The bot can show server information, user information, and bot information using embedded messages.

### Utility Commands

The bot includes coin flip, dice roll, and random number commands for simple server activities.

## Tech Stack

| Technology | Purpose |
| --- | --- |
| Python | Main programming language |
| discord.py | Discord API wrapper and bot framework |
| python-dotenv | Loads the bot token from `.env` |
| JSON | Stores configurable server settings |
| Discord Slash Commands | Provides command interface inside Discord |
| Cogs | Organizes bot features into modules |

## System Workflow

1. The user starts the bot by running `python bot.py`.
2. The bot loads the token from `.env`.
3. The bot reads server settings from `config.json`.
4. The bot loads all cog files from the `cogs` folder.
5. Slash commands are synced with Discord.
6. Users run commands inside Discord.
7. Permission checks confirm whether the user can perform the action.
8. The command runs and sends a response.
9. Important moderation actions are sent to the configured log channel.
10. Event-based features, such as bad-word filtering and welcome messages, run automatically when Discord events occur.

## Module Description

| File | Description |
| --- | --- |
| `bot.py` | Main bot startup file. Loads environment variables, cogs, and slash commands. |
| `cogs/moderation.py` | Moderation commands and bad-word filter. |
| `cogs/roles.py` | Role commands, secret role, and reaction-role system. |
| `cogs/interaction.py` | Hello, ping, say, 8-ball, and DM commands. |
| `cogs/tickets.py` | Ticket creation and ticket closing system. |
| `cogs/polls.py` | Poll command with emoji reactions. |
| `cogs/welcome.py` | Welcome and goodbye event messages. |
| `cogs/info.py` | Server, user, and bot information commands. |
| `cogs/utility.py` | Coin flip, dice, and random number commands. |
| `utils/config_loader.py` | Loads and saves `config.json`. |
| `utils/checks.py` | Shared permission and role hierarchy checks. |
| `utils/logger.py` | Sends log messages to the configured log channel. |

## Security and Safety

- The bot token is stored in `.env`, not in source code.
- `.env` is ignored by Git.
- Permission checks protect moderation and role commands.
- Role hierarchy checks prevent the bot from managing roles or users it should not manage.
- Log messages help staff review important moderation actions.

## Future Scope

- Add a database for permanent warning history.
- Add automatic moderation levels, such as repeated-warning punishments.
- Add ticket transcripts before deleting ticket channels.
- Add a dashboard for editing configuration values.
- Add command usage analytics for administrators.
- Add scheduled announcements and reminders.
- Add multilingual support for server messages.

## Conclusion

This Discord bot provides a practical server management system with moderation, roles, tickets, polls, welcome messages, and utility commands. The project demonstrates Python programming, API integration, modular design, permission handling, event handling, and secure configuration management.

Because the bot is divided into cogs and utility modules, it can be extended easily in the future without rewriting the main application.
