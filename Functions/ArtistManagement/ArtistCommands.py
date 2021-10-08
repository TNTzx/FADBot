import discord
import discord.ext.commands as cmds
import tldextract as tld

from Functions.ArtistManagement import ArtistControlFunctions as acf


defaultImage = "https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg"

async def proof(ctx):
    return await acf.waitForResponse(ctx, 
        "Please send proof that you contacted the artist.",
        "Take a screenshot of the email/message that the artist sent you that proves the artist's verification/unverification. You can only upload 1 image/link.",
        acf.OutputTypes.image
    )

async def availability(ctx):
    availability = await acf.waitForResponse(ctx,
        "Is the artist verified, disallowed, or does it vary between songs?",
        "\"Verified\" means that the artist's songs are allowed to be used for custom PA levels.\n\"Disallowed\" means that the artist's songs cannot be used.\n\"Varies\" means that it depends per song, for example, remixes aren't allowed for use but all their other songs are allowed.",
        acf.OutputTypes.text, choices=["Verified", "Disallowed", "Varies"]
    )
    availabilityCorrespondence = {
        "verified": 0,
        "disallowed": 1,
        "varies": 3
    }
    return availabilityCorrespondence[availability]

async def name(ctx):
    return await acf.waitForResponse(ctx,
        "Artist Name",
        "Send the artist name.",
        acf.OutputTypes.text
    )

async def aliases(ctx):
    aliasNames = await acf.waitForResponse(ctx,
        "Artist Aliases",
        "Send other names that the artist goes by.",
        acf.OutputTypes.listing, skippable=True, skipDefault=[]
    )
    return [{"name": alias} for alias in aliasNames]

async def description(ctx):
    return await acf.waitForResponse(ctx,
        "Send a small description about the artist.",
        "You can put information about the artist here.",
        acf.OutputTypes.text, skippable=True, skipDefault="I'm an artist!"
    )

async def notes(ctx):
    return await acf.waitForResponse(ctx,
        "Notes",
        "Send other notes you want to put in.",
        acf.OutputTypes.text, skippable=True
    )

async def avatar(ctx):
    return await acf.waitForResponse(ctx,
        "Send an image to an avatar of the artist.",
        "This is the profile picture that the artist uses.",
        acf.OutputTypes.image, skippable=True, skipDefault=defaultImage
    )

async def banner(ctx):
    return await acf.waitForResponse(ctx,
        "Send an image to the banner of the artist.",
        "This is the banner that the artist uses.",
        acf.OutputTypes.image, skippable=True, skipDefault=defaultImage
    )

async def tracks(ctx):
    return await acf.waitForResponse(ctx,
        "How many tracks does the artist have?",
        "This is the count for how much music the artist has produced. It can easily be found on Soundcloud pages, if you were wondering.",
        acf.OutputTypes.number, skippable=True, skipDefault=0
    )

async def genre(ctx):
    return await acf.waitForResponse(ctx,
        "What is the genre of the artist?",
        "This is the type of music that the artist makes.",
        acf.OutputTypes.text, skippable=True, skipDefault="Mixed"
    )


async def usageRights(ctx, availability):
    usageRights = await acf.waitForResponse(ctx,
        "What are the usage rights for the artist?",
        "This is where you put in the usage rights. For example, if remixes aren't allowed, you can type in `\"Remixes: Disallowed\"`. Add more items as needed.",
        acf.OutputTypes.dictionary, choicesDict=["Verified", "Disallowed"], skippable=True, skipDefault={}
    )
    usageList = []
    usageList.append({
            "name": "All songs",
            "value": True if availability == 0 else False
        })
    for right, state in usageRights.items():
        value = state == "verified"
        usageList.append({
            "name": right,
            "value": value
        })
    return usageList

async def socials(ctx):
    socials = await acf.waitForResponse(ctx,
        "Please put some links for the artist's social media here.",
        "This is where you put in links for the artist's socials such as Youtube, Spotify, Bandcamp, etc.",
        acf.OutputTypes.links, skippable=True, skipDefault=[]
    )
    socialList = []
    for link in socials:
        typeLink = tld.extract(link).domain
        typeLink = typeLink.capitalize()
        socialList.append({
            "url": link,
            "type": typeLink
        })
    return socialList