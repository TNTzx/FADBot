import discord
import discord.ext.commands as cmds
import asyncio

import requests as req
import tldextract as tld

import main
from Functions import CustomExceptions as ce
from Functions import ExtraFunctions as ef
from Functions.ArtistManagement import ArtistDataFormat as adf
from Functions.ArtistManagement import ArtistControlFunctions as acf


timeout = 60 * 2
defaultImage = "https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg"

class WaitFor:
    async def waitForResponse(self, ctx, title, description, outputType, choices=[], choicesDict=[], skippable=False, skipDefault=""):
        async def checkIfHasRequired():
            return len(choices) > 0
        async def checkIfHasRequiredDict():
            return len(choicesDict) > 0

        async def reformat(response: discord.Message):
            async def number():
                if not response.content.isnumeric():
                    await acf.sendError(ctx, "That's not a number!")
                    return None
                return int(response.content)

            async def text():
                if await checkIfHasRequired():
                    if not response.content.lower() in [x.lower() for x in choices]:
                        await acf.sendError(ctx, "You didn't send a choice in the list of choices!")
                        return None
                    return response.content.lower()
                if response.content == "":
                    await acf.sendError(ctx, "You didn't send anything!")
                    return None
                return response.content

            async def links():
                async def checkLink(url):
                    try:
                        imageRequest = req.head(url)
                    except Exception as exc:
                        await acf.sendError(ctx, f"You didn't send valid links! Here's the error:\n```{str(exc)}```")
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
                        await acf.sendError(ctx, f"You didn't send a valid image/link! Here's the error:\n```{str(exc)}```")
                        return None

                    if not imageRequest.headers["Content-Type"] in [f"image/{x}" for x in supportedFormats]:
                        await acf.sendError(ctx, f"You sent a link to an unsupported file format! The formats allowed are `{'`, `'.join(supportedFormats)}`.")
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
                        await acf.sendError(ctx, "Your formatting is wrong!")
                        return None

                    if not item[1].lower() in [x.lower() for x in choicesDict]:
                        await acf.sendError(ctx, f"Check if the right side of the colons contain these values: `{'`, `'.join([x for x in choicesDict])}`")
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

            response = await acf.waitFor(ctx)

            if response.content == f"{main.commandPrefix}cancel":
                raise ce.ExitFunction("Exited Function.")
            elif response.content == f"{main.commandPrefix}skip":
                if skippable:
                    await ctx.author.send("Section skipped.")
                    return skipDefault
                else:
                    await acf.sendError(ctx, "You can't skip this section!")
                    continue

            try:
                response = await reformat(response)
            except Exception as exc:
                await self.deleteIsUsingCommand(ctx.author.id)
                raise exc
            success = (response == None)
        return response

class OutputTypes():
        number = {"type": "number", "prefix": "a", "example": "1234531"}
        text = {"type": "text", "prefix": "some", "example": "This is a very cool string of text!"}
        links = {"type": "links", "prefix": "a list of", "example": "https://www.youtube.com/FunnyArtistName\nhttps://open.spotify.com/AnotherFunnyArtistName"}
        image = {"type": "image", "prefix": "an", "example": "https://cdn.discordapp.com/attachments/888419023237316609/894910496199827536/beanss.jpg`\n`(OR you can upload your images as attachments like normal!)"}
        listing = {"type": "list", "prefix": "a", "example": "This is the first item on the list!\nThis is the second item on the list!\nThis is the third item on the list!"}
        dictionary = {"type": "dictionary", "prefix": "a", "example": "Remixes: Unverified\nAll other songs: Verified\nA song I'm not sure of: Unknown"}


class ArtistData:
    def __init__(self):
        self.status = 0
        self.availability = 0
        self.id = None
        self.name = ""
        self.aliases = []
        self.description = "I am a contacted artist! :D"
        self.notes = "None"
        self.avatar = defaultImage
        self.banner = defaultImage
        self.tracks = 0
        self.genre = "Mixed"
        self.usageRights = {
                "name": "All songs",
                "value": True
            }
        self.socials = {}

class Artist:
    def __init__(self):
        self.proof = defaultImage
        self.vadbPage = "https://fadb.live/"
        self.artistData = ArtistData()

class User:
    def __init__(self):
        self.id = None


class Submission(WaitFor):
    def __init__(self):
        self.user = User()
        self.artist = Artist()
    

    async def setProof(self, ctx, skippable=False):
        self.artist.proof = await self.waitForResponse(ctx, 
            "Please send proof that you contacted the artist.",
            "Take a screenshot of the email/message that the artist sent you that proves the artist's verification/unverification. You can only upload 1 image/link.",
            acf.OutputTypes.image,
            skippable=skippable, skipDefault=self.artist.proof
        )
    
    async def setAvailability(self, ctx, skippable=False):
        availability = await self.waitForResponse(ctx,
            "Is the artist verified, disallowed, or does it vary between songs?",
            "\"Verified\" means that the artist's songs are allowed to be used for custom PA levels.\n\"Disallowed\" means that the artist's songs cannot be used.\n\"Varies\" means that it depends per song, for example, remixes aren't allowed for use but all their other songs are allowed.",
            acf.OutputTypes.text, choices=["Verified", "Disallowed", "Varies"],
            skippable=skippable, skipDefault=None
        )
        availabilityCorrespondence = {
            "verified": 0,
            "disallowed": 1,
            "varies": 3,
            None: self.artist.artistData.availability
        }
        self.artist.artistData.availability = availabilityCorrespondence[availability]

    async def setName(self, ctx, skippable=False):
        self.artist.artistData.name = await self.waitForResponse(ctx,
            "Artist Name",
            "Send the artist name.",
            acf.OutputTypes.text,
            skippable=skippable, skipDefault=self.artist.artistData.name
        )

    async def setAliases(self, ctx, skippable=True):
        aliasNames = await self.waitForResponse(ctx,
            "Artist Aliases",
            "Send other names that the artist goes by.",
            acf.OutputTypes.listing,
            skippable=skippable, skipDefault=None
        )
        self.artist.artistData.aliases = [{"name": alias} for alias in aliasNames] if aliasNames == None else self.artist.artistData.aliases

    async def setDescription(self, ctx, skippable=True):
        self.artist.artistData.description = await self.waitForResponse(ctx,
            "Send a small description about the artist.",
            "You can put information about the artist here.",
            acf.OutputTypes.text,
            skippable=skippable, skipDefault=self.artist.artistData.description
        )

    async def setNotes(self, ctx, skippable=True):
        self.artist.artistData.notes = await self.waitForResponse(ctx,
            "Notes",
            "Send other notes you want to put in.",
            acf.OutputTypes.text,
            skippable=skippable, skipDefault=self.artist.artistData.notes
        )

    async def setAvatar(self, ctx, skippable=True):
        self.artist.artistData.avatar = await self.waitForResponse(ctx,
            "Send an image to an avatar of the artist.",
            "This is the profile picture that the artist uses.",
            acf.OutputTypes.image,
            skippable=skippable, skipDefault=self.artist.artistData.avatar
        )

    async def setBanner(self, ctx, skippable=True):
        self.artist.artistData.banner = await self.waitForResponse(ctx,
            "Send an image to the banner of the artist.",
            "This is the banner that the artist uses.",
            acf.OutputTypes.image,
            skippable=skippable, skipDefault=self.artist.artistData.banner
        )

    async def setTracks(self, ctx, skippable=True):
        self.artist.artistData.tracks = await self.waitForResponse(ctx,
            "How many tracks does the artist have?",
            "This is the count for how much music the artist has produced. It can easily be found on Soundcloud pages, if you were wondering.",
            acf.OutputTypes.number,
            skippable=skippable, skipDefault=self.artist.artistData.tracks
        )

    async def setGenre(self, ctx, skippable=True):
        self.artist.artistData.genre = await self.waitForResponse(ctx,
            "What is the genre of the artist?",
            "This is the type of music that the artist makes.",
            acf.OutputTypes.text,
            skippable=skippable, skipDefault=self.artist.artistData.genre
        )


    async def setUsageRights(self, ctx, skippable=True):
        usageRights = await self.waitForResponse(ctx,
            "What are the usage rights for the artist?",
            "This is where you put in the usage rights. For example, if remixes aren't allowed, you can type in `\"Remixes: Disallowed\"`. Add more items as needed.",
            acf.OutputTypes.dictionary, choicesDict=["Verified", "Disallowed"],
            skippable=skippable, skipDefault={}
        )
        usageList = []
        usageList.append({
                "name": "All songs",
                "value": True if self.artist.artistData.availability == 0 else False
            })
        for right, state in usageRights.items():
            value = state == "verified"
            usageList.append({
                "name": right,
                "value": value
            })
        self.artist.artistData.usageRights = usageList if len(usageList) > 1 else self.artist.artistData.usageRights

    async def setSocials(self, ctx, skippable=True):
        socials = await self.waitForResponse(ctx,
            "Please put some links for the artist's social media here.",
            "This is where you put in links for the artist's socials such as Youtube, Spotify, Bandcamp, etc.",
            acf.OutputTypes.links,
            skippable=True, skipDefault=[]
        )
        socialList = []
        for link in socials:
            typeLink = tld.extract(link).domain
            typeLink = typeLink.capitalize()
            socialList.append({
                "url": link,
                "type": typeLink
            })
        self.artist.artistData.socials = socialList if len(socialList) > 0 else self.artist.artistData.socials

    
    async def generateDict(self):
        data = adf.dataFormat
        data["userInfo"]["id"] = self.user.id
        data["artistInfo"]["proof"] = self.artist.proof
        data["artistInfo"]["vadbPage"] = self.artist.vadbPage
        data["artistInfo"]["data"]["status"] = self.artist.artistData.status
        data["artistInfo"]["data"]["availability"] = self.artist.artistData.availability
        data["artistInfo"]["data"]["name"] = self.artist.artistData.name
        data["artistInfo"]["data"]["aliases"] = self.artist.artistData.aliases
        data["artistInfo"]["data"]["description"] = self.artist.artistData.description
        data["artistInfo"]["data"]["avatar"] = self.artist.artistData.avatar
        data["artistInfo"]["data"]["banner"] = self.artist.artistData.banner
        data["artistInfo"]["data"]["tracks"] = self.artist.artistData.tracks
        data["artistInfo"]["data"]["genre"] = self.artist.artistData.genre
        data["artistInfo"]["data"]["usageRights"] = self.artist.artistData.usageRights
        data["artistInfo"]["data"]["socials"] = self.artist.artistData.socials
        return data
