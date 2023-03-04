from discord.ext import commands
from discord import app_commands
import discord


# TODO:
#   Check only original artist can change comms status
#

class Art(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # VISUAL ARTIST ONLY

    @app_commands.command(name="comms", description="Select your comms status")
    @app_commands.checks.has_role("Visual Artist")
    @app_commands.choices(
        option=[
            discord.app_commands.Choice(name="Open", value=0),
            discord.app_commands.Choice(name="Close", value=1)
        ]
    )
    async def comms(self, interaction: discord.Interaction,
                    option: discord.app_commands.Choice[int]):
        # Open Comms
        if option.value == 0:
            open_tag = discord.utils.get(interaction.channel.parent.available_tags, name="Open Comms")
            await interaction.channel.edit(applied_tags=[open_tag])

            await interaction.response.send_message(
                f"Opened Comms!")

        # Close Comms
        elif option.value == 1:
            close_tag = discord.utils.get(interaction.channel.parent.available_tags, name="Closed Comms")
            await interaction.channel.edit(applied_tags=[close_tag])

            await interaction.response.send_message(
                f"Closed Comms!")
        else:
            await interaction.response.send_message(f"Something broke in [comms] logic.")


async def setup(bot):
    await bot.add_cog(Art(bot))
