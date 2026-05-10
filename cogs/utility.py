"""Small utility and randomizer commands."""

from __future__ import annotations

import random

import discord
from discord import app_commands
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="coinflip", description="Flip a coin.")
    async def coin_flip(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f"The coin landed on **{random.choice(['heads', 'tails'])}**.")

    @app_commands.command(name="dice", description="Roll dice.")
    @app_commands.describe(sides="Sides per die", count="Number of dice")
    async def dice(
        self,
        interaction: discord.Interaction,
        sides: app_commands.Range[int, 2, 100] = 6,
        count: app_commands.Range[int, 1, 20] = 1,
    ) -> None:
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls)
        await interaction.response.send_message(f"Rolled: `{', '.join(map(str, rolls))}` | Total: **{total}**")

    @app_commands.command(name="randomnumber", description="Pick a random number in a range.")
    @app_commands.describe(minimum="Lowest possible number", maximum="Highest possible number")
    async def random_number(
        self,
        interaction: discord.Interaction,
        minimum: int = 1,
        maximum: int = 100,
    ) -> None:
        if minimum > maximum:
            await interaction.response.send_message("Minimum must be less than or equal to maximum.", ephemeral=True)
            return

        await interaction.response.send_message(f"Random number: **{random.randint(minimum, maximum)}**")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utility(bot))
