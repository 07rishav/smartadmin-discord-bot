"""Poll slash command with emoji reactions."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands


POLL_EMOJIS = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯"]
YES_NO_EMOJIS = ["👍", "👎"]


class Polls(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="poll", description="Create a poll with emoji reactions.")
    @app_commands.describe(
        question="Poll question",
        options="Optional choices separated by |, up to 10 choices",
    )
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(add_reactions=True, send_messages=True)
    async def poll(
        self,
        interaction: discord.Interaction,
        question: str,
        options: str = "",
    ) -> None:
        choices = [choice.strip() for choice in options.split("|") if choice.strip()]

        if not choices:
            embed = discord.Embed(title="Poll", description=question, color=discord.Color.blurple())
            await interaction.response.send_message(embed=embed)
            message = await interaction.original_response()
            for emoji in YES_NO_EMOJIS:
                await message.add_reaction(emoji)
            return

        if len(choices) > len(POLL_EMOJIS):
            await interaction.response.send_message("Polls can have at most 10 choices.", ephemeral=True)
            return

        description = "\n".join(f"{POLL_EMOJIS[index]} {choice}" for index, choice in enumerate(choices))
        embed = discord.Embed(title=question, description=description, color=discord.Color.blurple())
        embed.set_footer(text=f"Poll by {interaction.user}")

        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        for index in range(len(choices)):
            await message.add_reaction(POLL_EMOJIS[index])


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Polls(bot))
