"""Moderation slash commands and the bad-word filter."""

from __future__ import annotations

import re
from datetime import timedelta
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from utils.checks import bot_can_manage_member, moderator_check, user_can_manage_member
from utils.config_loader import get_config_id, load_config
from utils.logger import send_log


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _member_guard(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
    ) -> bool:
        assert interaction.guild is not None

        allowed, message = user_can_manage_member(interaction, member)
        if not allowed:
            await interaction.response.send_message(message, ephemeral=True)
            return False

        allowed, message = bot_can_manage_member(interaction.guild, member)
        if not allowed:
            await interaction.response.send_message(message, ephemeral=True)
            return False

        return True

    @app_commands.command(name="kick", description="Kick a member from the server.")
    @app_commands.describe(member="Member to kick", reason="Reason shown in the audit log")
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(kick_members=True)
    @moderator_check()
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = None,
    ) -> None:
        if not await self._member_guard(interaction, member):
            return

        reason = reason or f"Kicked by {interaction.user}"
        await member.kick(reason=reason)
        await interaction.response.send_message(f"Kicked {member.mention}.", ephemeral=True)
        await send_log(
            interaction.guild,
            "Member Kicked",
            f"{member.mention} was kicked by {interaction.user.mention}.",
            color=discord.Color.orange(),
            fields=[("Reason", reason, False)],
        )

    @app_commands.command(name="ban", description="Ban a member from the server.")
    @app_commands.describe(
        member="Member to ban",
        delete_message_days="How many days of their messages to delete",
        reason="Reason shown in the audit log",
    )
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(ban_members=True)
    @moderator_check()
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        delete_message_days: app_commands.Range[int, 0, 7] = 0,
        reason: Optional[str] = None,
    ) -> None:
        if not await self._member_guard(interaction, member):
            return

        reason = reason or f"Banned by {interaction.user}"
        await member.ban(reason=reason, delete_message_seconds=delete_message_days * 86400)
        await interaction.response.send_message(f"Banned {member.mention}.", ephemeral=True)
        await send_log(
            interaction.guild,
            "Member Banned",
            f"{member.mention} was banned by {interaction.user.mention}.",
            color=discord.Color.red(),
            fields=[("Reason", reason, False)],
        )

    @app_commands.command(name="unban", description="Unban a user by Discord user ID.")
    @app_commands.describe(user_id="Discord user ID to unban", reason="Reason shown in the audit log")
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(ban_members=True)
    @moderator_check()
    async def unban(
        self,
        interaction: discord.Interaction,
        user_id: str,
        reason: Optional[str] = None,
    ) -> None:
        assert interaction.guild is not None

        try:
            snowflake = int(user_id)
        except ValueError:
            await interaction.response.send_message("Please provide a valid numeric user ID.", ephemeral=True)
            return

        reason = reason or f"Unbanned by {interaction.user}"
        ban_entry = await interaction.guild.fetch_ban(discord.Object(id=snowflake))
        await interaction.guild.unban(ban_entry.user, reason=reason)
        await interaction.response.send_message(f"Unbanned `{ban_entry.user}`.", ephemeral=True)
        await send_log(
            interaction.guild,
            "Member Unbanned",
            f"`{ban_entry.user}` was unbanned by {interaction.user.mention}.",
            color=discord.Color.green(),
            fields=[("Reason", reason, False)],
        )

    @app_commands.command(name="mute", description="Timeout a member and optionally apply the configured muted role.")
    @app_commands.describe(
        member="Member to mute",
        minutes="Timeout duration in minutes",
        reason="Reason shown in the audit log",
    )
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    @moderator_check()
    async def mute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        minutes: app_commands.Range[int, 1, 40320] = 10,
        reason: Optional[str] = None,
    ) -> None:
        assert interaction.guild is not None
        if not await self._member_guard(interaction, member):
            return

        reason = reason or f"Muted by {interaction.user}"
        until = discord.utils.utcnow() + timedelta(minutes=minutes)
        await member.timeout(until, reason=reason)

        config = load_config()
        muted_role_id = get_config_id(config, "muted_role_id")
        muted_role = interaction.guild.get_role(muted_role_id) if muted_role_id else None
        if muted_role:
            try:
                await member.add_roles(muted_role, reason=reason)
            except discord.HTTPException:
                pass

        await interaction.response.send_message(f"Muted {member.mention} for {minutes} minutes.", ephemeral=True)
        await send_log(
            interaction.guild,
            "Member Muted",
            f"{member.mention} was muted by {interaction.user.mention}.",
            color=discord.Color.orange(),
            fields=[("Duration", f"{minutes} minutes", True), ("Reason", reason, False)],
        )

    @app_commands.command(name="unmute", description="Remove a member timeout and the configured muted role.")
    @app_commands.describe(member="Member to unmute", reason="Reason shown in the audit log")
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    @moderator_check()
    async def unmute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = None,
    ) -> None:
        assert interaction.guild is not None
        if not await self._member_guard(interaction, member):
            return

        reason = reason or f"Unmuted by {interaction.user}"
        await member.timeout(None, reason=reason)

        config = load_config()
        muted_role_id = get_config_id(config, "muted_role_id")
        muted_role = interaction.guild.get_role(muted_role_id) if muted_role_id else None
        if muted_role and muted_role in member.roles:
            try:
                await member.remove_roles(muted_role, reason=reason)
            except discord.HTTPException:
                pass

        await interaction.response.send_message(f"Unmuted {member.mention}.", ephemeral=True)
        await send_log(
            interaction.guild,
            "Member Unmuted",
            f"{member.mention} was unmuted by {interaction.user.mention}.",
            color=discord.Color.green(),
            fields=[("Reason", reason, False)],
        )

    @app_commands.command(name="warn", description="Warn a member and log the warning.")
    @app_commands.describe(member="Member to warn", reason="Warning reason")
    @app_commands.guild_only()
    @moderator_check()
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str,
    ) -> None:
        assert interaction.guild is not None

        allowed, message = user_can_manage_member(interaction, member)
        if not allowed:
            await interaction.response.send_message(message, ephemeral=True)
            return

        try:
            await member.send(f"You were warned in **{interaction.guild.name}**: {reason}")
            dm_status = "DM sent"
        except discord.HTTPException:
            dm_status = "Could not DM member"

        await interaction.response.send_message(f"Warned {member.mention}. {dm_status}.", ephemeral=True)
        await send_log(
            interaction.guild,
            "Member Warned",
            f"{member.mention} was warned by {interaction.user.mention}.",
            color=discord.Color.yellow(),
            fields=[("Reason", reason, False), ("DM", dm_status, True)],
        )

    @app_commands.command(name="clear", description="Bulk-delete recent messages from this channel.")
    @app_commands.describe(amount="Number of recent messages to delete")
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(manage_messages=True, read_message_history=True)
    @moderator_check()
    async def clear(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 1, 100],
    ) -> None:
        assert interaction.guild is not None

        channel = interaction.channel
        if not isinstance(channel, (discord.TextChannel, discord.Thread)):
            await interaction.response.send_message("This command only works in text channels.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        deleted = await channel.purge(limit=amount, reason=f"Cleared by {interaction.user}")
        await interaction.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)
        await send_log(
            interaction.guild,
            "Messages Cleared",
            f"{interaction.user.mention} cleared {len(deleted)} messages in {channel.mention}.",
            color=discord.Color.blurple(),
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or message.guild is None or not message.content:
            return

        config = load_config()
        bad_words = [word.strip().lower() for word in config.get("bad_words", []) if word.strip()]
        if not bad_words:
            return

        content = message.content.lower()
        # Whole-word matching avoids blocking harmless words that only contain a banned word.
        matched_word = next((word for word in bad_words if re.search(rf"\b{re.escape(word)}\b", content)), None)
        if not matched_word:
            return

        try:
            await message.delete()
        except discord.HTTPException:
            pass

        warning = f"{message.author.mention}, please avoid banned words in this server."
        try:
            await message.channel.send(warning, delete_after=8, allowed_mentions=discord.AllowedMentions(users=True))
        except discord.HTTPException:
            pass

        await send_log(
            message.guild,
            "Bad Word Filter",
            f"Deleted a message from {message.author.mention} in {message.channel.mention}.",
            color=discord.Color.red(),
            fields=[("Matched Word", matched_word, True), ("Message", message.content[:1000], False)],
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderation(bot))
