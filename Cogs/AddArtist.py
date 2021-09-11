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

    @commands.command(name="artistadd")
    async def artistadd(self, ctx, artistName, artistStatus, artistAvail):
        datas = {
            "name" : artistName,
            "status" : artistStatus,
            "availability" : artistAvail
        }
        print(apiCookie)
        response = requests.post(f"{apiLink}api/artist", data=datas, cookies=apiCookie)
        await ctx.send(f"```{response.json()}```")

def setup(bot):
    bot.add_cog(GetArtists(bot))



# , cookies=apiCookie