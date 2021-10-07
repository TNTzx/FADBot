import discord
import discord.ext.commands as cmds
import asyncio
import requests as req
import tldextract as tld

import main
from Functions import CustomExceptions as ce
from Functions import CommandWrappingFunction as cw
from Functions import ArtistControlFunctions as acf
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
        await acf.checkIfUsingCommand(ctx, ctx.author.id)
        fi.appendData(["artistData", "pending", "isUsingCommand"], [ctx.author.id])


        submission = {
            "userInfo": {
                "name": "UserName",
                "id": "UserId"
            },
            "artistInfo": {
                "proof": "png",
                "vadbpage": "page",
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
                        }
                    ],
                    "socials": [
                        { 
                            "url": "funnyurl",
                            "type": "type"
                        }
                    ]
                }
            }
        }

        await ctx.send("The verification submission has been moved to your DMs. Please check it.")
        await ctx.author.send("> The verification submission is now being set up. Please __follow the prompts as needed__.")

        defaultImage = "https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg"

        submission["userInfo"] = {
            "id": ctx.author.id
        }

        # submission["artistInfo"]["proof"] = await acf.waitForResponse(ctx, 
        #     "Please send proof that you contacted the artist.",
        #     "Take a screenshot of the email/message that the artist sent you that proves the artist's verification/unverification. You can only upload 1 image/link.",
        #     acf.OutputTypes.image
        # )

        # availability = await acf.waitForResponse(ctx,
        #     "Is the artist verified, disallowed, or does it vary between songs?",
        #     "\"Verified\" means that the artist's songs are allowed to be used for custom PA levels.\n\"Disallowed\" means that the artist's songs cannot be used.\n\"Varies\" means that it depends per song, for example, remixes aren't allowed for use but all their other songs are allowed.",
        #     acf.OutputTypes.text, choices=["Verified", "Disallowed", "Varies"]
        # )
        # if availability == "verified":
        #     submission["artistInfo"]["data"]["availability"] = 0
        # elif availability == "disallowed":
        #     submission["artistInfo"]["data"]["availability"] = 1
        # elif availability == "varies":
        #     submission["artistInfo"]["data"]["availability"] = 3
            
        submission["artistInfo"]["data"]["name"] = await acf.waitForResponse(ctx,
            "Send the name of the artist.",
            "This is the name of the artist.",
            acf.OutputTypes.text
        )
        # submission["artistInfo"]["data"]["description"] = await acf.waitForResponse(ctx,
        #     "Send a small description about the artist.",
        #     "You can put information about the artist here.",
        #     acf.OutputTypes.text, skippable=True, skipDefault="I'm an artist!"
        # )
        # submission["artistInfo"]["data"]["avatar"] = await acf.waitForResponse(ctx,
        #     "Send an image to an avatar of the artist.",
        #     "This is the profile picture that the artist uses.",
        #     acf.OutputTypes.image, skippable=True, skipDefault=defaultImage
        # )
        # submission["artistInfo"]["data"]["banner"] = await acf.waitForResponse(ctx,
        #     "Send an image to the banner of the artist.",
        #     "This is the banner that the artist uses.",
        #     acf.OutputTypes.image, skippable=True, skipDefault=defaultImage
        # )
        # submission["artistInfo"]["data"]["tracks"] = await acf.waitForResponse(ctx,
        #     "How many tracks does the artist have?",
        #     "This is the count for how much music the artist has produced. It can easily be found on Soundcloud pages, if you were wondering.",
        #     acf.OutputTypes.number, skippable=True, skipDefault=0
        # )
        # submission["artistInfo"]["data"]["genre"] = await acf.waitForResponse(ctx,
        #     "What is the genre of the artist?",
        #     "This is the type of music that the artist makes.",
        #     acf.OutputTypes.text, skippable=True, skipDefault="Mixed"
        # )


        # usageRights = await acf.waitForResponse(ctx,
        #     "What are the usage rights for the artist?",
        #     "This is where you put in the usage rights. For example, if remixes aren't allowed, you can type in `\"Remixes: Disallowed\"`. Add more items as needed.",
        #     acf.OutputTypes.dictionary, choicesDict=["Verified", "Disallowed"], skippable=True, skipDefault={}
        # )
        # usageList = []
        # usageList.append({
        #         "name": "All songs",
        #         "value": True if submission["artistInfo"]["data"]["availability"] == 0 else False
        #     })
        # for right, state in usageRights.items():
        #     value = True if state == "verified" else False
        #     usageList.append({
        #         "name": right,
        #         "value": value
        #     })
        # submission["artistInfo"]["data"]["usageRights"] = usageList

        # socials = await acf.waitForResponse(ctx,
        #     "Please put some links for the artist's social media here.",
        #     "This is where you put in links for the artist's socials such as Youtube, Spotify, Bandcamp, etc.",
        #     acf.OutputTypes.links, skippable=True, skipDefault=[]
        # )
        # socialList = []
        # for link in socials:
        #     typeLink = tld.extract(link).domain
        #     typeLink = typeLink.capitalize()
        #     socialList.append({
        #         "url": link,
        #         "type": typeLink
        #     })
        # submission["artistInfo"]["data"]["socials"] = socialList
            
        # print(submission)

        data = {'userInfo': {'id': 279803094722674693}, 'artistInfo': {'proof': 'https://cdn.discordapp.com/attachments/890222271849963571/895618409046343700/logo.png', 'vadbpage': 'https://cdn.discordapp.com/attachments/890222271849963571/895618409046343700/logo.png', 'data': {'name': 'quack', 'avatar': 'https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg', 'banner': 'https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg', 'description': 'quakc', 'tracks': 0, 'genre': 'Mixed', 'status': 0, 'availability': 3, 'notes': 'Notes, Optional', 'usageRights': [{'name': 'All songs', 'value': False}, {'name': 'beans', 'value': True}], 'socials': [{'url': 'https://www.youtube.com/watch?v=dWjP99xjy_A&list=WL&index=37&ab_channel=Ludwig', 'type': 'youtube'}]}}}

        await ctx.send(embed=await acf.generateEmbed(data))
        await acf.deleteIsUsingCommand(ctx, ctx.author.id)
        


    @cw.command(
        category=cw.Categories.botControl,
        description="Cancels the current command.",
        guildOnly=False
    )
    async def cancel(self, ctx: cmds.Context):
        if isinstance(ctx.channel, discord.DMChannel):
            await acf.deleteIsUsingCommand(ctx, ctx.author.id)
            await ctx.author.send("Command cancelled.")


def setup(bot):
    bot.add_cog(ArtistControl(bot))
