import discord
import discord.ext.commands as cmds
import asyncio
import requests as req

import main
from Functions import CustomExceptions as ce
from Functions import CommandWrappingFunction as cw
from Functions import ExtraFunctions as ef
from Functions import FirebaseInteraction as fi


class ArtistControl(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cw.command(
        category=cw.Categories.artistManagement,
        description=f"Requests an artist to be added to the database. Times out after `{ef.formatTime(60 * 2)}``.",
        aliases=["aa"]
    )
    async def artistadd(self, ctx: cmds.Context):

        async def checkIfUsingCommand(authorId):
            usersUsing = fi.getData(["artistData", "pending", "isUsingCommand"])
            if authorId in list(usersUsing):
                await ef.sendError(ctx, f"You're already using this command! Use {main.commandPrefix}cancel on your DMs with me to cancel the command.")
                raise ce.ExitFunction("Exited Function.")
        
        async def deleteIsUsingCommand():
            data = fi.getData(["artistData", "pending", "isUsingCommand"])
            data.remove(ctx.author.id)
            fi.editData(["artistData", "pending"], {"isUsingCommand": data})
        
        await checkIfUsingCommand(ctx.author.id)
        fi.appendData(["artistData", "pending", "isUsingCommand"], [ctx.author.id])


        class OutputTypes():
                text = {"type": "text", "prefix": "some", "example": "This is a very cool string of text!"}
                image = {"type": "image", "prefix": "an", "example": "https://cdn.discordapp.com/attachments/888419023237316609/894910496199827536/beanss.jpg`\n`OR you can upload your images as attachments like normal!"}
                listing = {"type": "list", "prefix": "a", "example": "This is the first item on the list!\nThis is the second item on the list!"}
                dictionary = {"type": "dictionary", "prefix": "a", "example": "All songs: Verified\nRemixes: Unverified"}

        async def waitForResponse(message: discord.Message, outputType, choices=[], skippable=False, skipDefault=""):
            async def sendError(suffix):
                await ef.sendError(ctx, f"{suffix} Try again.", sendToAuthor=True)
            async def checkIfHasRequired():
                return len(choices) > 0


            async def reformat(response: discord.Message):
                async def text():
                    if await checkIfHasRequired() and (not response.content.lower() in [x.lower() for x in choices]):
                        await sendError("You didn't send a choice in the list of choices!")
                        return None
                    if response.content == "":
                        await sendError("You didn't send anything!")
                        return None
                    return response.content
                
                async def image():
                    async def checkImage(imageUrl):
                        supportedFormats = ["png", "jpg", "jpeg"]

                        try:
                            imageRequest = req.head(imageUrl)
                        except Exception as exc:
                            await sendError(f"You didn't send a valid link! Here's the error:\n```{str(exc)}```")
                            return None

                        if not imageRequest.headers["Content-Type"] in [f"image/{x}" for x in supportedFormats]:
                            await sendError(f"You sent a link to an unsupported file format! The formats allowed are `{'`, `'.join(supportedFormats)}`.")
                            return None
                        
                        return imageUrl

                    async def attachments():
                        return await checkImage(response.attachments[0].url)
                            
                    async def link():
                        return await checkImage(response.content)


                    if not len(response.attachments) == 0:
                        return await attachments()
                    else:
                        return await link()

                async def listing():
                    return response.content.split("\n")

                async def dictionary():
                    entries = response.content.split("\n")
                    entryDict = {}
                    for entry in entries:
                        item = entry.split(":")
                        item = [x.lstrip(' ') for x in item]
                        try:
                            if not len(item) == 2:
                                raise IndexError

                            entryDict[item[0]] = item[1]

                        except (KeyError, IndexError):
                            await sendError("Your formatting is wrong!")
                            return None
                    return entryDict


                if outputType == OutputTypes.text:
                    return await text()
                elif outputType == OutputTypes.image:
                    return await image()
                elif outputType == OutputTypes.listing:
                    return await listing()
                elif outputType == OutputTypes.dictionary:
                    return await dictionary()
            

            success = True
            while success:
                embed = discord.Embed(title=message, description="_ _")

                embedName = f"You have to send {outputType['prefix']} {outputType['type']}!"

                if not await checkIfHasRequired():
                    embedDescription = f"__Here is an example of what you have to send:__\n\n`{outputType['example']}`"
                else:
                    embedDescription = f"Choose from one of the following choices: \n`{'`, `'.join(choices)}`"
                embed.add_field(name=embedName, value=embedDescription)

                skipStr = f"Use {main.commandPrefix}cancel to cancel the current command" + (f", or use {main.commandPrefix}skip to skip this section if you don't know what this is." if skippable else ".")
                embed.set_footer(text=skipStr)

                await ctx.author.send(embed=embed)


                try:
                    response = await main.bot.wait_for("message", check=lambda msg: ctx.author.id == msg.author.id and isinstance(msg.channel, discord.channel.DMChannel), timeout=60 * 2)
                except asyncio.TimeoutError:
                    await sendError(f"Command timed out. Please use {main.commandPrefix}artistadd again.")
                    raise ce.ExitFunction("Exited Function.")


                if response.content == f"{main.commandPrefix}cancel":
                    await deleteIsUsingCommand()
                    await ctx.author.send("Command cancelled.")
                    raise ce.ExitFunction("Exited Function.")
                elif response.content == f"{main.commandPrefix}skip":
                    if skippable:
                        await ctx.author.send("Section skipped.")
                        return skipDefault
                    else:
                        await sendError("You can't skip this!")
                        continue

                try:
                    response = await reformat(response)
                except Exception as exc:
                    await deleteIsUsingCommand()
                    raise exc
                success = (response == None)
            return response


        submission = {
            "userInfo": {
                "name": "UserName",
                "id": "UserId",
            },
            "artistInfo": {
                "proof": "png",
                "data": {
                    "name": "ArtistName",
                    "avatar": "AvatarLink",
                    "banner": "BannerLink, Optional",
                    "description": "Description",
                    "tracks": 1,
                    "genre": "Genre",
                    "status": 0,
                    "availability": 0,
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
            }
        }

        submission["artistInfo"]["proof"] = await waitForResponse("Please send proof that you contacted the artist. You may only upload 1 image.", OutputTypes.image)
        print(submission["artistInfo"]["proof"])


        await deleteIsUsingCommand()
        


def setup(bot):
    bot.add_cog(ArtistControl(bot))
