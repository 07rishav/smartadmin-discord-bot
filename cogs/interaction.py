"""Friendly interaction commands."""

from __future__ import annotations

import random
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from utils.checks import moderator_check
from utils.logger import send_log


EIGHT_BALL_ANSWERS = [
    "It is certain.",
    "Without a doubt.",
    "Yes.",
    "Ask again later.",
    "Cannot predict now.",
    "Do not count on it.",
    "My reply is no.",
    "Very doubtful.",
]


class Interaction(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="hello", description="Say hello to the bot.")
    async def hello(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f"Hello, {interaction.user.mention}!")

    @app_commands.command(name="ping", description="Show the bot latency.")
    async def ping(self, interaction: discord.Interaction) -> None:
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! `{latency_ms}ms`")

    @app_commands.command(name="say", description="Make the bot send a message.")
    @app_commands.describe(message="Message to send", channel="Optional destination channel")
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(send_messages=True)
    @moderator_check()
    async def say(
        self,
        interaction: discord.Interaction,
        message: str,
        channel: Optional[discord.TextChannel] = None,
    ) -> None:
        destination = channel or interaction.channel
        if not isinstance(destination, discord.TextChannel):
            await interaction.response.send_message("Choose a text channel for that message.", ephemeral=True)
            return

        await destination.send(message, allowed_mentions=discord.AllowedMentions.none())
        await interaction.response.send_message("Message sent.", ephemeral=True)

    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question.")
    @app_commands.describe(question="Your yes/no question")
    async def eight_ball(self, interaction: discord.Interaction, question: str) -> None:
        answer = random.choice(EIGHT_BALL_ANSWERS)
        embed = discord.Embed(title="Magic 8-Ball", color=discord.Color.dark_teal())
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=answer, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="dm", description="Send a direct message to a member.")
    @app_commands.describe(member="Member to DM", message="Message to send")
    @app_commands.guild_only()
    @moderator_check()
    async def dm(self, interaction: discord.Interaction, member: discord.Member, message: str) -> None:
        assert interaction.guild is not None

        try:
            await member.send(f"Message from **{interaction.guild.name}** staff:\n{message}")
        except discord.HTTPException:
            await interaction.response.send_message("I could not DM that member.", ephemeral=True)
            return

        await interaction.response.send_message(f"DM sent to {member.mention}.", ephemeral=True)
        await send_log(
            interaction.guild,
            "Staff DM Sent",
            f"{interaction.user.mention} sent a DM to {member.mention}.",
            color=discord.Color.blurple(),
            fields=[("Message", message[:1000], False)],
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Interaction(bot))
