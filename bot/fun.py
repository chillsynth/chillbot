from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if "resonance" in message.content.lower():
            print(f"Reacted 'resonance' to message: {message.jump_url}")
            await message.add_reaction("<:resonanceDEV:1020142646787837992>")
            # <:resonance:699652237135183982> Actual emoji_ID when integrated
            # <:resonanceDEV:1020142646787837992> TEST Emoji
        if "home" in message.content.lower():
            print(f"Reacted 'hom' to message: {message.jump_url}")
            await message.add_reaction("<homDEV:1062177710832635986>")
            # <:hom:1061464615260803192> Actual emoji_ID when integrated
            # <:homDEV:1062177710832635986> TEST Emoji
        if "eg" in message.content.lower():
            print(f"Reacted 'egem' to message: {message.jump_url}")
            await message.add_reaction("<:egemDEV:1062784474351403068>")
            # <:egem:852516812423430144> Actual emoji_ID when integrated
            # <:egemDEV:1062784474351403068> TEST Emoji


async def setup(bot):
    await bot.add_cog(Fun(bot))
