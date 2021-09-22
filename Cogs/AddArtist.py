import discord
from discord.ext import commands
import asyncio

from PIL import Image
import requests


import main

from Functions import functionsandstuff as fas
from Functions import customExceptions as cE
from Functions import requestnew

timeoutDuration = 60 * 2

class AddArtists(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    isUsingArtistAddCommand = []

    @commands.command(name="artistadd")
    async def artistadd(self, ctx:commands.Context):

        # check if user is already using the command
        if ctx.author.id in self.isUsingArtistAddCommand:
            await fas.sendError(ctx, f"You're already using this command! The command has been cancelled for you. Try {main.commandPrefix}artistadd again.")
            return
        else:
            self.isUsingArtistAddCommand.append(ctx.author.id)


        await ctx.author.send("> **The verified artist will now be set up here.**\nIf you mistyped something, you can edit it before the submission is sent, don't worry.")
        await ctx.send("You have been DM'ed. Please follow the instructions there.")

        async def sendCreate(prefix, expectedType="text", singleInput=True, skippable=False, outputAsDict=False, dictCheck="usageRights"):
            if outputAsDict:
                response = {}
            else:
                response = []

            defaultValue = ""
            if dictCheck == "usageRights":
                defaultValue = {"All songs:", "Verified"}
            

            # check if input is valid
            async def checkInput(message):
                nonlocal response
                if expectedType == "text":
                    if message.content == "":
                        await fas.sendError(ctx, "You didn't send a __text message__! Try again.", sendToAuthor=True)
                        return False

                    if outputAsDict:
                        textMain = []

                        textSplit1 = message.content.split(": ")
                        for i in textSplit1:
                            textSplit2 = i.split("\n")
                            for j in textSplit2:
                                textMain.append(j)
                        
                        if dictCheck == "usageRights":
                            validResponses = ["Verified", "Unverified"]
                            for i in textMain[1::2]:
                                if not (i in validResponses):
                                    await fas.sendError(ctx, "You sent an invalid response! Make sure that \"Verified\" or \"Unverified\" is capitalized correctly. Try again.", sendToAuthor=True)
                                    return False

                        response = dict(zip(textMain[::2], textMain[1::2]))

                    else:
                        response.append(message.content)

                    return True

                elif expectedType == "image":
                    imageExts = ["png", "jpeg", "jpg"]
                    url = []

                    # if input is a link
                    if not len(message.attachments) == 0:
                        if singleInput and not len(message.attachments) == 1:
                            await fas.sendError(ctx, "You sent more than one image! Please send only one. Try again.", sendToAuthor=True)

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
                    response = url
                    return True
                
                

            # main loop
            success = False
            while not success:
                if not skippable:
                    await ctx.author.send(f"{prefix}\nThis command will time out in `{await fas.formatTime(timeoutDuration)}`. Use `{main.commandPrefix}cancel` to cancel making a new verified artist.")
                else:
                    await ctx.author.send(f"{prefix}\nThis command will time out in `{await fas.formatTime(timeoutDuration)}`. Use `{main.commandPrefix}cancel` to cancel making a new verified artist. If you don't know what to do, use {main.commandPrefix}skip to skip this command.")

                try:
                    message : discord.Message = await main.bot.wait_for("message", check=lambda message: message.author == ctx.author, timeout=timeoutDuration)
                except asyncio.TimeoutError:
                    # timeout
                    await fas.sendError(ctx, f"Command timed out. Please use `{main.commandPrefix}artistadd` again.", sendToAuthor=True)
                    self.isUsingArtistAddCommand.remove(ctx.author.id)
                    raise cE.ExitFunction("Exited Function.")
                
                # checks for skips or cancels
                if message.content == f"{main.commandPrefix}cancel":
                    await ctx.author.send(f"Command cancelled.")
                    self.isUsingArtistAddCommand.remove(ctx.author.id)
                    raise cE.ExitFunction("Exited Function.")
                if skippable and message.content == f"{main.commandPrefix}skip":
                    await ctx.author.send(f"Command skipped, now using default values.")
                    return defaultValue
                
                success = await checkInput(message)

            # returns responses
            if singleInput and not outputAsDict:
                return response[0]
            else:
                return response
            


        # send stuff
        arData = {}

        formatOfData = {
            "name": "ArtistName",
            "avatar": "AvatarLink",
            "banner": "BannerLink, Optional",
            "description": "Description",
            "tracks": 1, #AmountOfTracks, int
            "genre": "Genre",
            "status": 0,
                # 0: Completed
                # 1: No contact
                # 2: Pending
                # 3: Requested
                # 99: nil
            "availability": 0,
                # 0: Verified
                # 1: Disallowed
                # 2: Contact required
                # 3: Varies
                # 99: nil
            "notes": "Notes, Optional",
            "usageRights": [
                {
                    "name": "NameOfAllowedSong",
                    "value": True
                },
                {
                    "name": "NameOfDisallowedSong",
                    "value": False
                }
            ],
            "socials": [
                { 
                    "url": "funnyurl",
                    "type": "type"
                },
                {
                    "url": "anotherfunnyurl",
                    "type": "type"
                }
            ]
        }

        arContactProof = await sendCreate("Please send an image (or images) to __prove that you have contacted the artist__. Image links also work.", expectedType="image", singleInput=False)
        arData["avatar"] = await sendCreate("Please send an image of the __artist's profile picture__.", expectedType="image")
        arData["name"] = await sendCreate("Please send __the name of the artist__.", expectedType="text")
        arData["usageRights"] = await sendCreate(
            """Please send __the usage rights for this artist__.
            The format is as follows:
            > <song list 1>: <Verified | Unverified>
            > <song list 2>: <Verified | Unverified>
            Example:
            > Remixes: Unverified
            > All other songs: Verified""",
            outputAsDict=True, skippable=True
        )
        print(arData["usageRights"])

        # ar = discord.Embed(name="Example", thumbnail=arData["avatar"], colour=discord.Colour.gold())
        # ar.set_author(name=f"Artist data for {arData['name']}:", icon_url=arData["avatar"])

        # await ctx.author.send(embed=ar)

        # for i in arContactProof:
        #     await ctx.author.send(i)
        

        # remove user from "using list"
        self.isUsingArtistAddCommand.remove(ctx.author.id)



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
                await self.verifyArtist(reaction.message)
        else:
            print("beans")

    async def verifyArtist(message):
        return
    


def setup(bot):
    bot.add_cog(AddArtists(bot))