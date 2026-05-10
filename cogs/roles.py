"""Role management, secret role, and reaction-role system."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from utils.checks import bot_can_manage_role, moderator_check, user_can_manage_role
from utils.config_loader import get_config_id, load_config, save_config
from utils.logger import send_log


class Roles(commands.Cog):
    reactionrole = app_commands.Group(name="reactionrole", description="Manage reaction role mappings.")

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _role_guard(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
    ) -> bool:
        assert interaction.guild is not None

        allowed, message = user_can_manage_role(interaction, role)
        if not allowed:
            await interaction.response.send_message(message, ephemeral=True)
            return False

        allowed, message = bot_can_manage_role(interaction.guild, role)
        if not allowed:
            await interaction.response.send_message(message, ephemeral=True)
            return False

        return True

    @app_commands.command(name="addrole", description="Add a role to a member.")
    @app_commands.describe(member="Member to update", role="Role to add")
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @moderator_check()
    async def add_role(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        role: discord.Role,
    ) -> None:
        assert interaction.guild is not None
        if not await self._role_guard(interaction, role):
            return

        await member.add_roles(role, reason=f"Role added by {interaction.user}")
        await interaction.response.send_message(f"Added {role.mention} to {member.mention}.", ephemeral=True)
        await send_log(
            interaction.guild,
            "Role Added",
            f"{interaction.user.mention} added {role.mention} to {member.mention}.",
            color=discord.Color.green(),
        )

    @app_commands.command(name="removerole", description="Remove a role from a member.")
    @app_commands.describe(member="Member to update", role="Role to remove")
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @moderator_check()
    async def remove_role(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        role: discord.Role,
    ) -> None:
        assert interaction.guild is not None
        if not await self._role_guard(interaction, role):
            return

        await member.remove_roles(role, reason=f"Role removed by {interaction.user}")
        await interaction.response.send_message(f"Removed {role.mention} from {member.mention}.", ephemeral=True)
        await send_log(
            interaction.guild,
            "Role Removed",
            f"{interaction.user.mention} removed {role.mention} from {member.mention}.",
            color=discord.Color.orange(),
        )

    @app_commands.command(name="secretrole", description="Claim the configured private role with the secret password.")
    @app_commands.describe(password="Secret password from the server owner")
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def secret_role(self, interaction: discord.Interaction, password: str) -> None:
        assert interaction.guild is not None
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message("This command only works in a server.", ephemeral=True)
            return

        config = load_config()
        expected_password = str(config.get("secret_role_password", ""))
        role_id = get_config_id(config, "secret_role_id")
        role = interaction.guild.get_role(role_id) if role_id else None

        if not role:
            await interaction.response.send_message("The secret role is not configured yet.", ephemeral=True)
            return
        if password != expected_password or expected_password == "change-me":
            await interaction.response.send_message("Incorrect secret password.", ephemeral=True)
            return

        allowed, message = bot_can_manage_role(interaction.guild, role)
        if not allowed:
            await interaction.response.send_message(message, ephemeral=True)
            return

        await interaction.user.add_roles(role, reason="Secret role claimed")
        await interaction.response.send_message(f"You now have {role.mention}.", ephemeral=True)
        await send_log(
            interaction.guild,
            "Secret Role Claimed",
            f"{interaction.user.mention} claimed {role.mention}.",
            color=discord.Color.purple(),
        )

    @reactionrole.command(name="add", description="Bind an emoji reaction on a message to a role.")
    @app_commands.describe(channel="Channel containing the message", message_id="Message ID", emoji="Emoji to watch", role="Role to give")
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(manage_roles=True, read_message_history=True, add_reactions=True)
    @moderator_check()
    async def reaction_role_add(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message_id: str,
        emoji: str,
        role: discord.Role,
    ) -> None:
        assert interaction.guild is not None
        if not await self._role_guard(interaction, role):
            return

        try:
            message = await channel.fetch_message(int(message_id))
        except ValueError:
            await interaction.response.send_message("Message ID must be numeric.", ephemeral=True)
            return
        except discord.HTTPException:
            await interaction.response.send_message("I could not fetch that message.", ephemeral=True)
            return

        await message.add_reaction(emoji)

        config = load_config()
        reaction_roles = config.setdefault("reaction_roles", {})
        reaction_roles.setdefault(str(message.id), {})[emoji] = role.id
        save_config(config)

        await interaction.response.send_message(
            f"Reaction role saved: `{emoji}` on message `{message.id}` gives {role.mention}.",
            ephemeral=True,
        )

    @reactionrole.command(name="remove", description="Remove an emoji-to-role reaction-role mapping.")
    @app_commands.describe(message_id="Message ID", emoji="Emoji mapping to remove")
    @app_commands.guild_only()
    @moderator_check()
    async def reaction_role_remove(
        self,
        interaction: discord.Interaction,
        message_id: str,
        emoji: str,
    ) -> None:
        config = load_config()
        reaction_roles = config.setdefault("reaction_roles", {})
        mappings = reaction_roles.get(message_id, {})

        if emoji not in mappings:
            await interaction.response.send_message("That reaction-role mapping does not exist.", ephemeral=True)
            return

        del mappings[emoji]
        if not mappings:
            reaction_roles.pop(message_id, None)
        save_config(config)

        await interaction.response.send_message("Reaction-role mapping removed.", ephemeral=True)

    @reactionrole.command(name="list", description="List configured reaction-role mappings.")
    @app_commands.guild_only()
    @moderator_check()
    async def reaction_role_list(self, interaction: discord.Interaction) -> None:
        config = load_config()
        reaction_roles = config.get("reaction_roles", {})
        if not reaction_roles:
            await interaction.response.send_message("No reaction roles are configured.", ephemeral=True)
            return

        lines: list[str] = []
        for message_id, mappings in reaction_roles.items():
            for emoji, role_id in mappings.items():
                lines.append(f"Message `{message_id}` + `{emoji}` -> <@&{role_id}>")

        await interaction.response.send_message("\n".join(lines[:25]), ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        # Raw reaction events work even when the reacted message is not cached.
        if payload.guild_id is None or payload.member is None or payload.member.bot:
            return

        config = load_config()
        role_id = config.get("reaction_roles", {}).get(str(payload.message_id), {}).get(str(payload.emoji))
        if not role_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        role = guild.get_role(int(role_id))
        if role is None:
            return

        try:
            await payload.member.add_roles(role, reason="Reaction role added")
        except discord.HTTPException:
            return

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        # Remove the role using the saved message ID and emoji mapping from config.json.
        if payload.guild_id is None:
            return

        config = load_config()
        role_id = config.get("reaction_roles", {}).get(str(payload.message_id), {}).get(str(payload.emoji))
        if not role_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None:
            try:
                member = await guild.fetch_member(payload.user_id)
            except discord.HTTPException:
                return

        if member.bot:
            return

        role = guild.get_role(int(role_id))
        if role is None:
            return

        try:
            await member.remove_roles(role, reason="Reaction role removed")
        except discord.HTTPException:
            return


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Roles(bot))
