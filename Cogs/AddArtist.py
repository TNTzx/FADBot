import discord
from discord.ext import commands
import main
from Cogs import ErrorHandling
from Functions import requestnew

apiLink = main.apiLink
errorPrefix = ErrorHandling.errorPrefix

class GetArtists(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="artistadd")
    async def artistadd(self, ctx, artistName, artistStatus, artistAvail):
        artistStatusList = ["completed", "nocontact", "pending", "requested"]
        if artistStatus in artistStatusList:
            artistStatusIndex = artistStatusList.index(artistStatus)
        else:
            await ctx.send(f"{errorPrefix}`\"{artistStatus}\"` is not a valid option!")
            return
    
        datas = {
            "name" : artistName,
            "status" : artistStatusIndex,
            "availability" : artistAvail
        }

        await ctx.send("Adding artist...")
        request = await requestnew.makeRequest("POST", "api/artist", datas)

        if request["code"] == 201:
            await ctx.send("Verification submitted. Please wait for a moderator to approve your submission.")
        else:
            await ctx.send(f"{errorPrefix}The request has failed. The output is shown below:```{request}```")

def setup(bot):
    bot.add_cog(GetArtists(bot))