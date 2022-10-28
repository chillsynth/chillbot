from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if "resonance" in message.content.lower():
            print("\nReacted resonance")
            await message.add_reaction("<:resonance:699652237135183982>")
            # <:resonance:699652237135183982> Actual emoji_ID when integrated
            # <:resonanceDEV:1020142646787837992> TEST Emoji


async def setup(bot):
    await bot.add_cog(Fun(bot))
