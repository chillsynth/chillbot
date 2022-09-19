import discord
from discord.ext import commands
from discord import app_commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="invite", description="Creates invite with parameters")
    async def invite(self, interaction: discord.Interaction):
        """Send feedback to the server team"""
        await interaction.response.send_modal(Invite())


class Invite(discord.ui.Modal, title='Feedback'):
    feedback = discord.ui.TextInput(
        label="What would you like to feedback?",
        style=discord.TextStyle.long,
        placeholder="Type your feedback here...",
        required=True,
        min_length=0,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        inv = await channel.create_invite(max_age=self.invite_age.Select.values, max_uses=uses)
        await interaction.response.send_message(f"Successfully created invite `{str(inv)}` for channel <#{channel.id}>",
                                                ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        print(error)


async def setup(bot):
    await bot.add_cog(Admin(bot))
