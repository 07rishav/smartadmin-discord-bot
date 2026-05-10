"""Ticket creation and closing commands."""

from __future__ import annotations

import asyncio
import re

import discord
from discord import app_commands
from discord.ext import commands

from utils.checks import is_moderator
from utils.config_loader import get_config_id, load_config
from utils.logger import send_log


def _ticket_channel_name(member: discord.Member) -> str:
    safe_name = re.sub(r"[^a-z0-9-]", "-", member.name.lower()).strip("-")
    safe_name = safe_name or "user"
    return f"ticket-{safe_name}-{member.id % 10000}"


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ticket", description="Create a private support ticket.")
    @app_commands.describe(reason="Short reason for opening the ticket")
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    async def ticket(self, interaction: discord.Interaction, reason: str = "No reason provided") -> None:
        assert interaction.guild is not None
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message("This command only works in a server.", ephemeral=True)
            return

        existing = discord.utils.get(
            interaction.guild.text_channels,
            topic=f"Ticket owner: {interaction.user.id}",
        )
        if existing:
            await interaction.response.send_message(f"You already have a ticket: {existing.mention}", ephemeral=True)
            return

        config = load_config()
        category_id = get_config_id(config, "ticket_category_id")
        category = interaction.guild.get_channel(category_id) if category_id else None
        if category is not None and not isinstance(category, discord.CategoryChannel):
            category = None

        overwrites: dict[discord.abc.Snowflake, discord.PermissionOverwrite] = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
            ),
            interaction.guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_channels=True,
            ),
        }

        moderator_role_id = get_config_id(config, "moderator_role_id")
        moderator_role = interaction.guild.get_role(moderator_role_id) if moderator_role_id else None
        if moderator_role:
            overwrites[moderator_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
            )

        # Permission overwrites make the ticket private to the opener, staff, and the bot.
        channel = await interaction.guild.create_text_channel(
            name=_ticket_channel_name(interaction.user),
            category=category,
            overwrites=overwrites,
            topic=f"Ticket owner: {interaction.user.id}",
            reason=f"Ticket opened by {interaction.user}",
        )

        embed = discord.Embed(
            title="Support Ticket",
            description=f"{interaction.user.mention}, staff will be with you soon.\n\nReason: {reason}",
            color=discord.Color.blurple(),
        )
        await channel.send(content=interaction.user.mention, embed=embed)
        await interaction.response.send_message(f"Created ticket: {channel.mention}", ephemeral=True)
        await send_log(
            interaction.guild,
            "Ticket Created",
            f"{interaction.user.mention} opened {channel.mention}.",
            color=discord.Color.blurple(),
            fields=[("Reason", reason, False)],
        )

    @app_commands.command(name="close", description="Close the current ticket channel.")
    @app_commands.describe(reason="Reason for closing the ticket")
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    async def close(self, interaction: discord.Interaction, reason: str = "No reason provided") -> None:
        assert interaction.guild is not None

        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel) or not channel.topic or not channel.topic.startswith("Ticket owner: "):
            await interaction.response.send_message("This command can only be used inside a ticket channel.", ephemeral=True)
            return

        owner_id = int(channel.topic.removeprefix("Ticket owner: ").strip())
        if interaction.user.id != owner_id and not is_moderator(interaction):
            await interaction.response.send_message("Only the ticket owner or staff can close this ticket.", ephemeral=True)
            return

        await interaction.response.send_message("Closing this ticket in 5 seconds.")
        await send_log(
            interaction.guild,
            "Ticket Closed",
            f"{channel.mention} was closed by {interaction.user.mention}.",
            color=discord.Color.orange(),
            fields=[("Reason", reason, False)],
        )
        await asyncio.sleep(5)
        await channel.delete(reason=f"Ticket closed by {interaction.user}: {reason}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Tickets(bot))
