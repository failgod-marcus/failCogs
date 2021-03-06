import discord
from discord.ext import commands
import random


class Keks:
    """
    The Keks Cog
    """
    def __init__(self, bot):
        self.bot = bot
        self.cookie_answers = [
            "Oh vielen Dank!",
            "Om nom nom :yum:",
            "Ich liebe Kekse! :laughing:",
            ":blush:"
        ]

    @commands.command(name="keks", pass_context=True)
    async def _give_cookie(self, ctx):
        """
        Give the bot a cookie
        """
        await self.bot.say(random.choice(self.cookie_answers))

def setup(bot):
    n = Keks(bot)
    bot.add_cog(n)
