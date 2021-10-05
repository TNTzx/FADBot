import discord
from discord.ext import commands
import main

class GetArtists(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="artistget")
    async def artistget(self, ctx, artistName):
        return

def setup(bot):
    bot.add_cog(GetArtists(bot))



