import discord
from discord.ext import commands
from discord import app_commands


class Moderation(commands.Cog):
    def __init__(self, bot):
        # Variables to pre-load
        self.vars_loaded = False
        self.get_vars()
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name='Report Message',
            callback=self.my_cool_context_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)

    def get_vars(self):
        if not self.vars_loaded:
            try:
                self.vars_loaded = True
            except AttributeError:
                return None

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"`Moderation` cog loaded")
        self.get_vars()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:  # Don't reply to itself. Could again be client for you
            return
        if not message.guild:
            if "!report" in message.content.lower():
                await message.channel.send('this is a resonance response')


    @staticmethod
    async def my_cool_context_menu(interaction: discord.Interaction, message: discord.Message) -> None:
        await interaction.response.send_message(
            f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
        )

        # Handle report by sending it into a log channel
        log_channel = discord.utils.get(interaction.guild.channels, name="moderator-chat")

        embed = discord.Embed(title='Reported Message')
        if message.content:
            embed.description = message.content

        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.timestamp = message.created_at

        url_view = discord.ui.View()
        url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

        await log_channel.send(f"<@360882903913201675>")  # Tag Moderators
        await log_channel.send(embed=embed, view=url_view)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
