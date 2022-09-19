from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if "resonance" in message.content.lower():
            print("Reacted resonance")
            await message.add_reaction("<:resonanceDEV:1020142646787837992>")
            # <:resonance:699652237135183982> Actual emoji_ID when integrated


async def setup(bot):
    await bot.add_cog(Fun(bot))
