"""Main entry point for the Discord bot."""

from __future__ import annotations

import logging
import os
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from utils.config_loader import get_config_id, load_config


BASE_DIR = Path(__file__).resolve().parent

COGS = [
    "cogs.moderation",
    "cogs.roles",
    "cogs.interaction",
    "cogs.tickets",
    "cogs.polls",
    "cogs.welcome",
    "cogs.info",
    "cogs.utility",
]


class CommunityBot(commands.Bot):
    """Bot subclass that loads cogs and syncs slash commands on startup."""

    def __init__(self) -> None:
        self.config = load_config()

        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        intents.message_content = True
        intents.messages = True
        intents.reactions = True

        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self) -> None:
        for cog in COGS:
            await self.load_extension(cog)
            logging.info("Loaded extension %s", cog)

        guild_id = get_config_id(self.config, "guild_id")
        if guild_id:
            # Guild sync is instant and useful while developing a server bot.
            guild = discord.Object(id=guild_id)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logging.info("Synced %s slash commands to guild %s", len(synced), guild_id)
        else:
            synced = await self.tree.sync()
            logging.info("Synced %s global slash commands", len(synced))

    async def on_ready(self) -> None:
        logging.info("Logged in as %s (%s)", self.user, self.user.id if self.user else "unknown")
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="slash commands")
        )


async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError,
) -> None:
    """Send clean slash-command errors instead of noisy tracebacks in chat."""

    original = getattr(error, "original", error)

    if isinstance(original, app_commands.MissingPermissions):
        message = "You do not have the required Discord permissions for this command."
    elif isinstance(original, app_commands.BotMissingPermissions):
        missing = ", ".join(original.missing_permissions)
        message = f"I am missing required permissions: `{missing}`."
    elif isinstance(original, app_commands.CheckFailure):
        message = str(original) or "You are not allowed to use this command."
    elif isinstance(original, discord.Forbidden):
        message = "Discord refused that action. Check my role position and permissions."
    elif isinstance(original, discord.NotFound):
        message = "I could not find the requested Discord object."
    elif isinstance(original, discord.HTTPException):
        message = "Discord returned an API error while running that command."
    else:
        logging.exception("Unhandled slash command error", exc_info=original)
        message = "Something went wrong while running that command."

    try:
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    except discord.HTTPException:
        logging.exception("Failed to send command error response")


def main() -> None:
    load_dotenv(BASE_DIR / ".env")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN is missing. Copy .env.example to .env and add your token.")

    bot = CommunityBot()
    bot.tree.on_error = on_app_command_error
    bot.run(token)


if __name__ == "__main__":
    main()
