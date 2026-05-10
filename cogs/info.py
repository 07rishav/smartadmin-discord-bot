"""Server, user, and bot information commands."""

from __future__ import annotations

import platform

import discord
from discord import app_commands
from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="serverinfo", description="Show information about this server.")
    @app_commands.guild_only()
    async def server_info(self, interaction: discord.Interaction) -> None:
        assert interaction.guild is not None
        guild = interaction.guild

        embed = discord.Embed(title=guild.name, color=discord.Color.blurple(), timestamp=discord.utils.utcnow())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Owner", value=f"<@{guild.owner_id}>", inline=True)
        embed.add_field(name="Members", value=str(guild.member_count), inline=True)
        embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="Channels", value=str(len(guild.channels)), inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(guild.created_at, style="F"), inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Show information about a user.")
    @app_commands.describe(member="Member to inspect")
    @app_commands.guild_only()
    async def user_info(
        self,
        interaction: discord.Interaction,
        member: discord.Member | None = None,
    ) -> None:
        member = member or interaction.user
        if not isinstance(member, discord.Member):
            await interaction.response.send_message("This command only works in a server.", ephemeral=True)
            return

        top_role = member.top_role.mention if member.top_role else "None"
        embed = discord.Embed(title=str(member), color=member.color, timestamp=discord.utils.utcnow())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=str(member.id), inline=True)
        embed.add_field(name="Top Role", value=top_role, inline=True)
        embed.add_field(name="Bot", value="Yes" if member.bot else "No", inline=True)
        embed.add_field(name="Joined", value=discord.utils.format_dt(member.joined_at, style="F") if member.joined_at else "Unknown", inline=False)
        embed.add_field(name="Created", value=discord.utils.format_dt(member.created_at, style="F"), inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="botinfo", description="Show information about the bot.")
    async def show_bot_info(self, interaction: discord.Interaction) -> None:
        app_info = await self.bot.application_info()
        latency_ms = round(self.bot.latency * 1000)

        embed = discord.Embed(title="Bot Info", color=discord.Color.blurple(), timestamp=discord.utils.utcnow())
        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(name="Owner", value=str(app_info.owner), inline=True)
        embed.add_field(name="Servers", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Latency", value=f"{latency_ms}ms", inline=True)
        embed.add_field(name="discord.py", value=discord.__version__, inline=True)
        embed.add_field(name="Python", value=platform.python_version(), inline=True)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Info(bot))
