"""Welcome and goodbye member events."""

from __future__ import annotations

import discord
from discord.ext import commands

from utils.config_loader import get_config_id, load_config
from utils.logger import resolve_channel


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        config = load_config()
        channel = await resolve_channel(member.guild, get_config_id(config, "welcome_channel_id"))
        if not isinstance(channel, discord.TextChannel):
            return

        embed = discord.Embed(
            title="Welcome!",
            description=f"{member.mention} joined **{member.guild.name}**.",
            color=discord.Color.green(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Member #{member.guild.member_count}")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        config = load_config()
        goodbye_channel_id = get_config_id(config, "goodbye_channel_id") or get_config_id(config, "welcome_channel_id")
        channel = await resolve_channel(member.guild, goodbye_channel_id)
        if not isinstance(channel, discord.TextChannel):
            return

        embed = discord.Embed(
            title="Goodbye",
            description=f"`{member}` left **{member.guild.name}**.",
            color=discord.Color.orange(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Welcome(bot))
