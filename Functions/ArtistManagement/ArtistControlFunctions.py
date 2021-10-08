import discord
import discord.ext.commands as cmds
import requests as req
import asyncio

import main
from Functions import ExtraFunctions as ef
from Functions import FirebaseInteraction as fi
from Functions import CustomExceptions as ce


async def checkIfUsingCommand(authorId):
    usersUsing = fi.getData(["artistData", "pending", "isUsingCommand"])
    return authorId in list(usersUsing)
    
async def addIsUsingCommand(authorId):
    fi.appendData(["artistData", "pending", "isUsingCommand"], [authorId])

async def deleteIsUsingCommand(authorId):
    data = fi.getData(["artistData", "pending", "isUsingCommand"])
    try:
        data.remove(authorId)
    except ValueError: pass
    fi.editData(["artistData", "pending"], {"isUsingCommand": data})


class OutputTypes():
        number = {"type": "number", "prefix": "a", "example": "1234531"}
        text = {"type": "text", "prefix": "some", "example": "This is a very cool string of text!"}
        links = {"type": "links", "prefix": "a list of", "example": "https://www.youtube.com/FunnyArtistName\nhttps://open.spotify.com/AnotherFunnyArtistName"}
        image = {"type": "image", "prefix": "an", "example": "https://cdn.discordapp.com/attachments/888419023237316609/894910496199827536/beanss.jpg`\n`(OR you can upload your images as attachments like normal!)"}
        listing = {"type": "list", "prefix": "a", "example": "This is the first item on the list!\nThis is the second item on the list!\nThis is the third item on the list!"}
        dictionary = {"type": "dictionary", "prefix": "a", "example": "Remixes: Unverified\nAll other songs: Verified\nA song I'm not sure of: Unknown"}


timeout = 60 * 10
async def waitForResponse(ctx, title, description, outputType, choices=[], choicesDict=[], skippable=False, skipDefault=""):
    async def sendError(suffix):
        await ef.sendError(ctx, f"{suffix} Try again.", sendToAuthor=True)
    async def checkIfHasRequired():
        return len(choices) > 0
    async def checkIfHasRequiredDict():
        return len(choicesDict) > 0

    async def reformat(response: discord.Message):
        async def number():
            if not response.content.isnumeric():
                await sendError("That's not a number!")
                return None
            return int(response.content)

        async def text():
            if await checkIfHasRequired():
                if not response.content.lower() in [x.lower() for x in choices]:
                    await sendError("You didn't send a choice in the list of choices!")
                    return None
                return response.content.lower()
            if response.content == "":
                await sendError("You didn't send anything!")
                return None
            return response.content

        async def links():
            async def checkLink(url):
                try:
                    imageRequest = req.head(url)
                except Exception as exc:
                    await sendError(f"You didn't send valid links! Here's the error:\n```{str(exc)}```")
                    return None
                return url
            
            links = response.content.split("\n")
            for link in links:
                link = await checkLink(link)
                if link == None:
                    return None
            return links
            
        async def image():
            async def checkImage(imageUrl):
                supportedFormats = ["png", "jpg", "jpeg"]

                try:
                    imageRequest = req.head(imageUrl)
                except Exception as exc:
                    await sendError(f"You didn't send a valid image/link! Here's the error:\n```{str(exc)}```")
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

                    if not await checkIfHasRequiredDict():
                        entryDict[item[0]] = item[1]
                    else:
                        entryDict[item[0]] = item[1].lower()
                except (KeyError, IndexError):
                    await sendError("Your formatting is wrong!")
                    return None

                if not item[1].lower() in [x.lower() for x in choicesDict]:
                    await sendError(f"Check if the right side of the colons contain these values: `{'`, `'.join([x for x in choicesDict])}`")
                    return None
            return entryDict

        if outputType == OutputTypes.number:
            return await number()
        elif outputType == OutputTypes.text:
            return await text()
        elif outputType == OutputTypes.links:
            return await links()
        elif outputType == OutputTypes.image:
            return await image()
        elif outputType == OutputTypes.listing:
            return await listing()
        elif outputType == OutputTypes.dictionary:
            return await dictionary()
    

    success = True
    while success:
        title = title if not skippable else f"{title} (skippable)"
        embed = discord.Embed(title=title, description=description)
        embed.add_field(name="_ _", value="_ _", inline=False)

        fieldName = f"You have to send {outputType['prefix']} {outputType['type']}!"

        if not await checkIfHasRequired():
            fieldDesc = f"__Here is an example of what you have to send:__\n`{outputType['example']}`"
            embed.add_field(name=fieldName, value=fieldDesc, inline=False)
        else:
            fieldDesc = f"Choose from one of the following choices: \n`{'`, `'.join(choices)}`"
            embed.add_field(name=fieldName, value=fieldDesc, inline=False)
        
        embed.add_field(name="_ _", value="_ _", inline=False)

        skipStr = f"This command times out in {ef.formatTime(timeout)}. \nUse {main.commandPrefix}cancel to cancel the current command." + (f"\nUse {main.commandPrefix}skip to skip this section." if skippable else "")
        embed.set_footer(text=skipStr)

        await ctx.author.send(embed=embed)


        try:
            response = await main.bot.wait_for("message", check=lambda msg: ctx.author.id == msg.author.id and isinstance(msg.channel, discord.channel.DMChannel), timeout=timeout)
            ef.otherData = response
        except asyncio.TimeoutError:
            await sendError(f"Command timed out. Please use {main.commandPrefix}artistadd again.")
            raise ce.ExitFunction("Exited Function.")


        if response.content == f"{main.commandPrefix}cancel":
            raise ce.ExitFunction("Exited Function.")
        elif response.content == f"{main.commandPrefix}skip":
            if skippable:
                await ctx.author.send("Section skipped.")
                return skipDefault
            else:
                await sendError("You can't skip this section!")
                continue

        try:
            response = await reformat(response)
        except Exception as exc:
            await deleteIsUsingCommand(ctx, ctx.author.id)
            raise exc
        success = (response == None)
    return response


statusKeys = {
    0: "Completed",
    1: "No Contact",
    2: "Pending",
    3: "Requested"
}

availabilityKeys = {
    0: "Verified",
    1: "Disallowed",
    2: "Contact Required",
    3: "Varies"
}

colorKeys = {
    "Green": 0x00FF00,
    "Red": 0xFF0000,
    "Yellow": 0xFFFF00,
    "Blue": 0x0000FF
}

async def generateEmbed(data):
    description = data['artistInfo']['data']['description']

    artName = data['artistInfo']['data']['name']
    artVadbPage = data['artistInfo']['vadbpage']
    artAvatar = data['artistInfo']['data']['avatar']
    artBanner = data['artistInfo']['data']['banner']

    artAliases = data['artistInfo']['data']['aliases']
    aliasList = [alias["name"] for alias in artAliases]
    artAliases = f"`{'`, `'.join(aliasList)}`"

    artId = data['artistInfo']['data']['id']
    artId = artId if not artId == None else "Unknown"

    if not data['userInfo']['id'] == None:
        user: discord.User = await main.bot.fetch_user(data['userInfo']['id'])
        userName = f"{user.name}#{user.discriminator}"
        userId = user.id
    else:
        userName = "Unknown"
        userId = "Unknown"

    status = statusKeys[data['artistInfo']['data']['status']]
    availability = availabilityKeys[data['artistInfo']['data']['availability']]

    if status == "Completed":
        if availability == "Verified":
            color = colorKeys["Green"]
        elif availability == "Disallowed":
            color = colorKeys["Red"]
        elif availability == "Contact Required":
            color = colorKeys["Yellow"]
        elif availability == "Varies":
            color = colorKeys["Blue"]
    elif status == "No Contact":
        color = colorKeys["Yellow"]

    usageRights = data['artistInfo']['data']['usageRights']
    usageList = []
    for entry in usageRights:
        statusRights = entry["value"]
        usageList.append(f"{entry['name']}: {'Verified' if statusRights else 'Disallowed'}")
    usageRights = "\n".join(usageList)

    socials = data['artistInfo']['data']['socials']
    socialsList = []
    for entry in socials:
        link, domain = entry["url"], entry["type"]
        socialsList.append(f"[{domain}]({link})")
    socials = " ".join(socialsList)

    notes = data['artistInfo']['data']['notes']
    

    embed = discord.Embed(title=f"Artist data for {artName}:", description="_ _", color=color)
    embed.set_author(name=f"{artName} (ID: {artId})", url=artVadbPage, icon_url=artAvatar)
    embed.set_thumbnail(url=artAvatar)
    embed.set_image(url=artBanner)
    embed.set_footer(text=f"Verification submitted by {userName} ({userId}).")

    embed.add_field(name="Name:", value=f"**{artName}**")
    embed.add_field(name="Aliases:", value=artAliases)

    embed.add_field(name="Description:", value=description, inline=False)
    embed.add_field(name="VADB Page:", value=f"[Click here!]({artVadbPage})", inline=False)

    embed.add_field(name="Status:", value=status)
    if status == "Completed":
        embed.add_field(name="Availability:", value=f"**__{availability}__**")
        embed.add_field(name="Specific usage rights:", value=f"`{usageRights}`")
    
    embed.add_field(name="Social links:", value=socials, inline=False)

    embed.add_field(name="Other notes:", value=notes)

    return embed