import discord
from discord.ext import commands
import os
import asyncio
import requests
import json
import main
from Functions import requestnew

apiLink = main.apiLink

class GetArtists(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="artistadd")
    async def artistadd(self, ctx, artistName, artistStatus, artistAvail):
        artistStatusList = ["completed", "nocontact", "pending", "requested"]
        if artistStatus in artistStatusList:
            artistStatusIndex = artistStatusList.index(artistStatus)
        else:
            await ctx.send(f"Error! `\"{artistStatus}\"` is not a valid option!")
            return

        datas = {
            "name" : artistName,
            "status" : artistStatus,
            "availability" : artistAvail
        }
        request = await requestnew.makeRequest("POST", "api/artist", datas)
        await ctx.send(f"```{request}```")

def setup(bot):
    bot.add_cog(GetArtists(bot))