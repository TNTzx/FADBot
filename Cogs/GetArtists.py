import discord
from discord.ext import commands
import os
import asyncio
import requests
import json
import main

apiLink = main.apiLink
apiCookie = main.apiCookie

class GetArtists(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="artistget")
    async def artistget(self, ctx, artistName):
        response = requests.get(f"{apiLink}api/artist/{artistName}", headers=apiCookie)
        await ctx.send(f"```{response.json()}```")

def setup(bot):
    bot.add_cog(GetArtists(bot))



