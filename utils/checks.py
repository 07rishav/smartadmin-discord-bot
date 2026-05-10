"""Reusable slash-command checks and Discord hierarchy helpers."""

from __future__ import annotations

import discord
from discord import app_commands

from utils.config_loader import get_config_id, load_config


def is_moderator(interaction: discord.Interaction) -> bool:
    """Allow server managers/admins or the configured moderator role."""

    if interaction.guild is None or not isinstance(interaction.user, discord.Member):
        return False

    permissions = interaction.user.guild_permissions
    if permissions.administrator or permissions.manage_guild or permissions.moderate_members:
        return True

    moderator_role_id = get_config_id(load_config(), "moderator_role_id")
    return bool(moderator_role_id and any(role.id == moderator_role_id for role in interaction.user.roles))


def moderator_check() -> app_commands.Check:
    async def predicate(interaction: discord.Interaction) -> bool:
        if not is_moderator(interaction):
            raise app_commands.CheckFailure("Only moderators can use this command.")
        return True

    return app_commands.check(predicate)


def bot_can_manage_member(guild: discord.Guild, member: discord.Member) -> tuple[bool, str | None]:
    """Check whether the bot role is high enough to affect a member."""

    me = guild.me
    if me is None:
        return False, "I could not resolve my server member."
    if member == me:
        return False, "I cannot moderate myself."
    if member.top_role >= me.top_role and guild.owner_id != me.id:
        return False, "That member's top role is higher than or equal to my top role."
    return True, None


def user_can_manage_member(
    interaction: discord.Interaction,
    member: discord.Member,
) -> tuple[bool, str | None]:
    """Prevent moderators from acting on peers, higher roles, owners, or themselves."""

    if interaction.guild is None or not isinstance(interaction.user, discord.Member):
        return False, "This command can only be used in a server."
    if member.id == interaction.guild.owner_id:
        return False, "The server owner cannot be moderated."
    if member == interaction.user:
        return False, "You cannot use that action on yourself."
    if interaction.user.id != interaction.guild.owner_id and member.top_role >= interaction.user.top_role:
        return False, "You cannot moderate a member with an equal or higher top role."
    return True, None


def bot_can_manage_role(guild: discord.Guild, role: discord.Role) -> tuple[bool, str | None]:
    me = guild.me
    if me is None:
        return False, "I could not resolve my server member."
    if role.is_default():
        return False, "The everyone role cannot be assigned or removed."
    if role.managed:
        return False, "Managed integration roles cannot be changed manually."
    if role >= me.top_role:
        return False, "That role is higher than or equal to my top role."
    return True, None


def user_can_manage_role(
    interaction: discord.Interaction,
    role: discord.Role,
) -> tuple[bool, str | None]:
    if interaction.guild is None or not isinstance(interaction.user, discord.Member):
        return False, "This command can only be used in a server."
    if interaction.user.id != interaction.guild.owner_id and role >= interaction.user.top_role:
        return False, "You cannot manage a role higher than or equal to your top role."
    return True, None
