"""Shared moderation/action logging helpers."""

from __future__ import annotations

from typing import Iterable

import discord

from utils.config_loader import get_config_id, load_config


async def resolve_channel(guild: discord.Guild, channel_id: int | None) -> discord.abc.GuildChannel | None:
    if not channel_id:
        return None

    channel = guild.get_channel(channel_id)
    if channel is not None:
        return channel

    try:
        return await guild.fetch_channel(channel_id)
    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
        return None


async def send_log(
    guild: discord.Guild,
    title: str,
    description: str,
    *,
    color: discord.Color = discord.Color.blurple(),
    fields: Iterable[tuple[str, str, bool]] | None = None,
) -> None:
    """Send an embed to the configured log channel if one is set."""

    config = load_config()
    channel = await resolve_channel(guild, get_config_id(config, "log_channel_id"))
    if not isinstance(channel, discord.TextChannel):
        return

    embed = discord.Embed(title=title, description=description, color=color, timestamp=discord.utils.utcnow())
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

    try:
        await channel.send(embed=embed)
    except discord.HTTPException:
        return
