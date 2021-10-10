import discord
import discord.ext.commands as cmds
import requests as req
import asyncio

import main
from Functions import ExtraFunctions as ef
from Functions import FirebaseInteraction as fi
from Functions import CustomExceptions as ce
from Functions.ArtistManagement import SubmissionClass as sc


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

async def sendError(ctx, suffix):
    await ef.sendError(ctx, f"{suffix} Try again.", sendToAuthor=True)

timeout = 60 * 10
async def waitFor(ctx):
    try:
        response: discord.Message = await main.bot.wait_for("message", check=lambda msg: ctx.author.id == msg.author.id and isinstance(msg.channel, discord.channel.DMChannel), timeout=timeout)
        ef.otherData = response
    except asyncio.TimeoutError:
        await ef.sendError(f"Command timed out. Please use {main.commandPrefix}artistadd again.")
        raise ce.ExitFunction("Exited Function.")
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

async def generateEmbed(submission: sc.Submission):
    description = submission.artist.artistData.description

    artName = submission.artist.artistData.name
    artVadbPage = submission.artist.vadbPage
    artAvatar = submission.artist.artistData.avatar
    artBanner = submission.artist.artistData.banner

    artAliases = submission.artist.artistData.aliases
    aliasList = [alias["name"] for alias in artAliases]
    artAliases = f"`{'`, `'.join(aliasList)}`"

    artId = submission.artist.artistData.id
    artId = artId if not artId == None else "Unknown"

    if not submission.user.id == None:
        user: discord.User = await main.bot.fetch_user(submission['userInfo']['id'])
        userName = f"{user.name}#{user.discriminator}"
        userId = user.id
    else:
        userName = "Unknown"
        userId = "Unknown"

    status = statusKeys[submission.artist.artistData.status]
    availability = availabilityKeys[submission.artist.artistData.availability]

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

    usageRights = submission.artist.artistData.usageRights
    usageList = []
    for entry in usageRights:
        statusRights = entry["value"]
        usageList.append(f"{entry['name']}: {'Verified' if statusRights else 'Disallowed'}")
    usageRights = "\n".join(usageList)

    socials = submission.artist.artistData.socials
    socialsList = []
    for entry in socials:
        link, domain = entry["url"], entry["type"]
        socialsList.append(f"[{domain}]({link})")
    socials = " ".join(socialsList)

    notes = submission.artist.artistData.notes
    

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