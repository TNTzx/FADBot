import discord
from discord.ext import commands
import asyncio

from PIL import Image
import requests


import main

from Functions import functionsandstuff as fas
from Functions import customExceptions as cE
from Functions import requestnew


apiLink = main.apiLink
timeoutDuration = 120

class GetArtists(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    isUsingArtistAddCommand = []

    @commands.command(name="artistadd")
    async def artistadd(self, ctx:commands.Context):

        # check if user is already using the command
        if ctx.author.id in GetArtists.isUsingArtistAddCommand:
            await fas.sendError(ctx, f"You're already using this command! The command has been cancelled for you. Try {main.commandPrefix}artistadd again.")
            return
        else:
            GetArtists.isUsingArtistAddCommand.append(ctx.author.id)


        await ctx.author.send("> **The verified artist will now be set up here.**")
        await ctx.send("You have been DM'ed. Please follow the instructions there.")

        async def sendCreate(prefix, expectedType="text"):
            response = []

            # check if input is valid
            async def checkInput(message, expectedType):
                if expectedType == "text":
                    if message.content == "":
                        await fas.sendError(ctx, "You didn't send a __text message__! Try again.", sendToAuthor=True)
                        return False
                    response.append("text")
                    return True
                if expectedType == "image":
                    imageExts = ["png", "jpeg", "jpg"]
                    url = []

                    # if input is a link
                    if not len(message.attachments) == 0:
                        for i in message.attachments:
                            for image in imageExts:
                                if i.url.endswith(image):
                                    break

                                if imageExts.index(image) == (len(imageExts) - 1):
                                    await fas.sendError(ctx, f"You didn't send an __image__ or a __link to an image__!\nMake sure the image is in the following formats: `{', '.join(imageExts)}`. Try again.", sendToAuthor=True)
                                    return False
                            url.append(i.url)
                    # if input is an attachment
                    else:
                        for image in imageExts:
                            if message.content.endswith(image):
                                break

                            if imageExts.index(image) == (len(imageExts) - 1):
                                await fas.sendError(ctx, f"You didn't send an __image__ or a __link to an image__!\nMake sure the image is in the following formats: `{', '.join(imageExts)}`. Try again.", sendToAuthor=True)
                                return False
                        url.append(message.content)
                    response.append(url)
                    return True


            # main loop
            success = False
            while not success:
                await ctx.author.send(f"{prefix}\nThis command will time out in `{await fas.formatTime(timeoutDuration)}`. Use `{main.commandPrefix}cancel` to cancel making a new verified artist.")
                try:
                    message : discord.Message = await main.bot.wait_for("message", check=lambda message: message.author == ctx.author, timeout=timeoutDuration)
                except asyncio.TimeoutError:
                    # timeout
                    await fas.sendError(ctx, f"Command timed out. Please use `{main.commandPrefix}artistadd` again.", sendToAuthor=True)
                    GetArtists.isUsingArtistAddCommand.remove(ctx.author.id)
                    raise cE.ExitFunction("Exited Function.")
                
                if message.content == f"{main.commandPrefix}cancel":
                    # cancelled
                    await ctx.author.send(f"Command cancelled.")
                    GetArtists.isUsingArtistAddCommand.remove(ctx.author.id)
                    raise cE.ExitFunction("Exited Function.")
                
                success = await checkInput(message, expectedType)

            # returns responses
            if expectedType == "text":
                return response[0]
            elif expectedType == "image":
                return response
            

        # send stuff
        rpContactProof = await sendCreate("\n Please send an __image (or images)__ to prove that you have contacted the artist.", "image")
        rpArtistName = await sendCreate("\n Please send the name of the artist.", "text")
        

        # remove user from "using list"
        GetArtists.isUsingArtistAddCommand.remove(ctx.author.id)



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