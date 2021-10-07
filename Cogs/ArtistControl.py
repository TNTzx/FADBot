import discord
import discord.ext.commands as cmds
import asyncio

import main
from Functions import CustomExceptions as ce
from Functions import CommandWrappingFunction as cw
from Functions import ExtraFunctions as ef

class ArtistControl(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cw.command(
        category=cw.Categories.artistManagement,
        description=f"Requests an artist to be added to the database. Times out after `{ef.formatTime(60 * 2)}``.",
        aliases=["aa"]
    )
    async def artistadd(self, ctx: cmds.Context):

        class OutputTypes():
                text = {"type": "text", "prefix": "some", "example": "This is a very cool string of text!"}
                image = {"type": "image", "prefix": "an", "example": "https://cdn.discordapp.com/attachments/888419023237316609/894910496199827536/beanss.jpg`\n`OR you can upload your images as attachments like normal!"}
                listing = {"type": "list", "prefix": "a", "example": "This is the first item on the list!\nThis is the second item on the list!"}
                dictionary = {"type": "dictionary", "prefix": "a", "example": "All songs: Verified\nRemixes: Unverified"}

        async def waitForResponse(message: discord.Message, outputType, skippable=False, skipDefault=""):
            async def sendError(suffix):
                await ef.sendError(ctx, f"{suffix} Try again.", sendToAuthor=True)

            async def reformat(response: discord.Message):
                async def text():
                    if response.content == "":
                        await sendError("You didn't send anything!")
                        return None
                    return response.content
                
                async def image():
                    async def attachments():
                        return [attachment.url for attachment in response.attachments]
                            
                    async def link():
                        supportedFormats = ["png", "jpg", "jpeg"]
                        if not response.content.endswith(tuple(supportedFormats)):
                            await sendError(f"You sent a link to an unsupported file format! The formats allowed are `{'`, `'.join(supportedFormats)}` for links.")
                            return None
                        return [response.content]


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
                embedExample = f"__Here is an example of what you have to send:__\n\n`{outputType['example']}`"
                embed.add_field(name=embedName, value=embedExample)

                skipStr = f"Use {main.commandPrefix}cancel to cancel the current command" + (f", or use {main.commandPrefix}skip to skip this section if you don't know what this is." if skippable else ".")
                embed.set_footer(text=skipStr)

                await ctx.author.send(embed=embed)


                try:
                    response = await main.bot.wait_for("message", check=lambda msg: ctx.author.id == msg.author.id and isinstance(msg.channel, discord.channel.DMChannel), timeout=60 * 2)
                except asyncio.TimeoutError:
                    await sendError(f"Command timed out. Please use {main.commandPrefix}artistadd again.")
                    raise ce.ExitFunction("Exited Function.")


                if response.content == f"{main.commandPrefix}cancel":
                    await ctx.author.send("Command cancelled.")
                    raise ce.ExitFunction("Exited Function.")
                elif response.content == f"{main.commandPrefix}skip":
                    if skippable:
                        await ctx.author.send("Section skipped.")
                        return skipDefault
                    else:
                        await sendError("You can't skip this!")
                        continue

                response = await reformat(response)
                success = (response == None)
            return response


        # response = await waitForResponse("Text test", OutputTypes.text)
        # await ctx.send(response)
        # response = await waitForResponse("Image test", OutputTypes.image)
        # await ctx.send(response)
        response = await waitForResponse("List test", OutputTypes.listing, skippable=True, skipDefault=[])
        await ctx.send(response)
        response = await waitForResponse("Dictionary test", OutputTypes.dictionary)
        await ctx.send(response)


def setup(bot):
    bot.add_cog(ArtistControl(bot))
