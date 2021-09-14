import discord
from discord.ext import commands
import main

from Functions import functionsandstuff as fas
from Functions import requestnew

apiLink = main.apiLink
timeoutDuration = 60

class GetArtists(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="artistadd")
    async def artistadd(self, ctx):
        await ctx.author.send("> **The verified artist will now be set up here.**")
        await ctx.send("You have been DM'ed. Please follow the instructions there.")

        async def sendCreate(prefix):
            await ctx.author.send(f"{prefix}\nThis command will time out in `{await fas.formatTime(timeoutDuration)}`. Use `{main.commandPrefix}cancel` to cancel making a new verified artist.")
            message = await main.bot.wait_for("message", timeout=timeoutDuration)
            return message

        await sendCreate("\n Please send an image to prove that you have contacted the artist.")
        


        # artistStatusList = ["completed", "nocontact", "pending", "requested"]
        # if artistStatus in artistStatusList:
        #     artistStatusIndex = artistStatusList.index(artistStatus)
        # else:
        #     await fas.sendError(ctx, f"`\"{artistStatus}\"` is not a valid option!")
        #     return
    
        # datas = {
        #     "name" : artistName,
        #     "status" : artistStatusIndex,
        #     "availability" : artistAvail
        # }

        # await ctx.send("Adding artist...")
        # request = await requestnew.makeRequest("POST", "api/artist", datas)

        # if request["code"] == 201:
        #     await ctx.send("Verification submitted. Please wait for a moderator to approve your submission.")
        # else:
        #     await fas.sendError(ctx, f"The request has failed. The output is shown below:```{request}```", sendToOwner=True)
    

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction:discord.Reaction, user):
        userRoleList = []
        for role in user.roles:
            userRoleList.append(role.name)
            
        if main.adminRole in userRoleList:
            if reaction.emoji == main.verifyEmote:
                await GetArtists.verifyArtist(reaction.message)
        else:
            print("beans")

    async def verifyArtist(message):
        return
    


def setup(bot):
    bot.add_cog(GetArtists(bot))