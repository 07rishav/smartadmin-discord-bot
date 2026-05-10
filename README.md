# Discord.py Community Bot

A complete modular Discord server management bot built with Python and `discord.py` 2.x. The bot uses slash commands, a cog-based project structure, a JSON configuration file, and a `.env` token file so sensitive credentials are not hardcoded.

## Project Highlights

- Slash-command based Discord bot
- Moderation tools for kick, ban, unban, mute, unmute, warn, and message clearing
- Bad-word filter with automatic message deletion, user warning, and log message
- Role tools including add role, remove role, secret private role, and reaction roles
- Interaction commands such as hello, ping, say, 8-ball, and DM
- Ticket system with private support channels and close command
- Poll system using emoji reactions
- Welcome and goodbye messages
- Server, user, and bot information commands
- Utility commands for coin flip, dice roll, and random number
- Configurable channel IDs, role IDs, bad words, ticket category, and reaction roles
- Modular cogs for clean code organization

## Folder Structure

```text
bot.py
.env.example
.gitignore
config.json
requirements.txt
README.md
COMMANDS.md
PROJECT_REPORT.md
cogs/
  moderation.py
  roles.py
  interaction.py
  tickets.py
  polls.py
  welcome.py
  info.py
  utility.py
utils/
  config_loader.py
  checks.py
  logger.py
```

## Requirements

- Python 3.10 or newer
- A Discord account
- A Discord server where you have permission to add bots
- A Discord bot application created in the Discord Developer Portal

## Discord Developer Portal Setup

1. Open the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application**.
3. Give the application a name.
4. Open the **Bot** section.
5. Click **Add Bot** if a bot is not already created.
6. Click **Reset Token** or **Copy Token** and keep the token private.
7. Enable these privileged gateway intents:
   - Server Members Intent
   - Message Content Intent
8. Save the changes.

## Invite the Bot to a Server

1. In the Discord Developer Portal, open your application.
2. Go to **OAuth2** > **URL Generator**.
3. Select these scopes:
   - `bot`
   - `applications.commands`
4. Select these recommended bot permissions:
   - Kick Members
   - Ban Members
   - Moderate Members
   - Manage Messages
   - Manage Roles
   - Manage Channels
   - Read Message History
   - Send Messages
   - Add Reactions
5. Copy the generated invite URL.
6. Open the URL in your browser and invite the bot to your server.

Important: the bot role must be above the roles it needs to assign, remove, mute, kick, or ban.

## Local Setup

1. Open a terminal in the project folder:

```bash
cd /Users/rishavkumar/Documents/Codex/2026-05-10/build-a-complete-discord-bot-in
```

2. Create a virtual environment:

```bash
python3 -m venv .venv
```

3. Activate the virtual environment:

```bash
source .venv/bin/activate
```

On Windows, use:

```bash
.venv\Scripts\activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Create the `.env` file from the example:

```bash
cp .env.example .env
```

6. Open `.env` and add your real Discord bot token:

```env
DISCORD_TOKEN=your-real-token-here
```

Do not share this token and do not upload `.env` to GitHub.

## Config Setup

Open `config.json` and replace the example values with IDs from your Discord server.

```json
{
  "guild_id": 123456789012345678,
  "log_channel_id": 123456789012345678,
  "welcome_channel_id": 123456789012345678,
  "goodbye_channel_id": 123456789012345678,
  "ticket_category_id": 123456789012345678,
  "moderator_role_id": 123456789012345678,
  "muted_role_id": 123456789012345678,
  "secret_role_id": 123456789012345678,
  "secret_role_password": "your-secret-password",
  "bad_words": ["word1", "word2"],
  "reaction_roles": {}
}
```

### How to Copy Discord IDs

1. Open Discord.
2. Go to **User Settings** > **Advanced**.
3. Enable **Developer Mode**.
4. Right-click a server, channel, role, user, or message.
5. Click **Copy ID**.

### Config Fields

- `guild_id`: server ID for fast slash-command syncing. Use `0` for global sync.
- `log_channel_id`: channel where moderation and filter logs are sent.
- `welcome_channel_id`: channel for welcome messages.
- `goodbye_channel_id`: channel for goodbye messages. If unset, the welcome channel is used.
- `ticket_category_id`: category where ticket channels are created.
- `moderator_role_id`: role allowed to use moderator commands.
- `muted_role_id`: optional muted role added during `/mute`.
- `secret_role_id`: private role given by `/secretrole`.
- `secret_role_password`: password users must enter for `/secretrole`.
- `bad_words`: list of blocked words for the message filter.
- `reaction_roles`: message, emoji, and role mappings for reaction roles.

## Running the Bot

Start the bot with:

```bash
python bot.py
```

If setup is correct, the terminal will show that the bot logged in and synced slash commands.

## Testing Checklist

After the bot is online, test these items in a private test server:

- `/ping` responds with latency.
- `/hello` sends a greeting.
- `/serverinfo`, `/userinfo`, and `/botinfo` show embed information.
- A configured bad word is deleted and logged.
- `/ticket` creates a private channel and `/close` deletes it.
- `/poll` creates reactions.
- `/addrole` and `/removerole` work when the bot role is high enough.
- `/reactionrole add` saves a mapping and users receive/remove roles by reacting.

## Command Reference

See [COMMANDS.md](COMMANDS.md) for the full command list and purpose of each command.

## College Report

See [PROJECT_REPORT.md](PROJECT_REPORT.md) for the project introduction, objectives, features, tech stack, workflow, future scope, and conclusion.

## Common Issues

### Slash Commands Do Not Appear

- Make sure the bot was invited with the `applications.commands` scope.
- Set `guild_id` in `config.json` to your server ID for faster command syncing.
- Restart the bot after changing `config.json`.

### Bot Cannot Add or Remove Roles

- Move the bot role above the role it needs to manage.
- Make sure the bot has the **Manage Roles** permission.

### Bad-Word Filter Does Not Work

- Enable **Message Content Intent** in the Developer Portal.
- Restart the bot after enabling the intent.

### Welcome Messages Do Not Work

- Enable **Server Members Intent** in the Developer Portal.
- Check that `welcome_channel_id` is correct.

## Security Notes

- The Discord token is loaded from `.env`.
- `.env` is ignored by Git.
- `.env.example` is safe to share because it does not contain a real token.
- Never post your token in screenshots, GitHub, reports, or chat messages.

## Dependencies

Dependencies are listed in `requirements.txt`:

```text
discord.py
python-dotenv
```
