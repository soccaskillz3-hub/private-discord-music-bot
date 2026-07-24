import discord
from discord.ext import commands
from discord import app_commands
from database.database import add_user, remove_user, get_users

from config import OWNER_ID


class Owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(
        name="authorize",
        description="Authorize a user to use the music bot"
    )
    async def authorize(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                "❌ You are not the owner.",
                ephemeral=True
            )
            return

        await add_user(member.id)

        await interaction.response.send_message(
            f"✅ {member.mention} has been authorized."
        )


    @app_commands.command(
        name="revoke",
        description="Remove a user's access"
    )
    async def revoke(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                "❌ You are not the owner.",
                ephemeral=True
            )
            return

        await remove_user(member.id)

        await interaction.response.send_message(
            f"✅ {member.mention} has been removed."
        )

    @app_commands.command(
        name="authorized",
        description="Show all authorized users"
    )
    async def authorized(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                "❌ You are not the owner.",
                ephemeral=True
            )
            return

        users = await get_users()

        if not users:
            await interaction.response.send_message(
                "No authorized users."
            )
            return

        message = "🔒 Authorized Users:\n"

        for user_id in users:
            user = self.bot.get_user(user_id)

            if user:
                message += f"• {user.name}\n"
            else:
                message += f"• {user_id}\n"

        await interaction.response.send_message(message)

async def setup(bot):
    await bot.add_cog(Owner(bot))
