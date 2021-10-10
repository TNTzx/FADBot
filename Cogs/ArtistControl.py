import discord
import discord.ext.commands as cmds
import asyncio
import requests as req
import tldextract as tld

import main
from Functions import CustomExceptions as ce
from Functions import CommandWrappingFunction as cw
from Functions import ExtraFunctions as ef
from Functions import FirebaseInteraction as fi
from Functions.ArtistManagement import SubmissionClass as sc
from Functions.ArtistManagement import ArtistDataFormat as adf


class ArtistControl(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot  


    @cw.command(
        category=cw.Categories.artistManagement,
        description=f"Requests an artist to be added to the database. Times out after `{ef.formatTime(60 * 2)}``.",
        aliases=["aa"],
        guildOnly=False
    )
    async def artistadd(self, ctx: cmds.Context):
        if await sc.ArtistFunctions.checkIfUsingCommand(sc.ArtistFunctions(), ctx.author.id):
            await ef.sendError(ctx, f"You're already using this command! Use {main.commandPrefix}cancel on your DMs with me to cancel the command.")
            raise ce.ExitFunction("Exited Function.")

        await sc.ArtistFunctions.addIsUsingCommand(sc.ArtistFunctions(), ctx.author.id)

        subm = sc.Submission()

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send("The verification submission has been moved to your DMs. Please check it.")

        await ctx.author.send("> The verification submission is now being set up. Please __follow the prompts as needed__.")

        # subm.user.id = ctx.author.id
        # await subm.setProof(ctx)
        # await subm.setAvailability(ctx)
        # await subm.setName(ctx)
        # await subm.setAliases(ctx)
        # await subm.setDescription(ctx)
        # await subm.setAvatar(ctx)
        # await subm.setBanner(ctx)
        # await subm.setTracks(ctx)
        # await subm.setGenre(ctx)
        # await subm.setUsageRights(ctx)
        # await subm.setSocials(ctx)

        testdata = {
            'userInfo': {
                'id': 279803094722674693
                }, 
            'artistInfo': {
                'proof': 'https://cdn.discordapp.com/attachments/890222271849963571/896719549536292914/236-2368062_24-mar-2009-quarter-circle-black-and-white_1.png', 
                'vadbPage': 'https://fadb.live/', 
                'data': {
                    'id': None, 
                    'name': 'quack', 
                    'aliases': [], 
                    'avatar': 'https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg', 
                    'banner': 'https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg', 
                    'description': 'I am a contacted artist! :D', 
                    'tracks': 0, 
                    'genre': 'Mixed', 
                    'status': 0, 
                    'availability': 0, 
                    'notes': 'text', 
                    'usageRights': [{
                        'name': 'All songs', 
                        'value': True
                    }], 
                    'socials': [{
                        "url": "https://www.example.com",
                        "type": "No added links!"
                    }]
                }
            }
        }

        await subm.generateFromDict(testdata)

        await subm.editLoop(ctx)
        await subm.deleteIsUsingCommand(ctx.author.id)
        


    @cw.command(
        category=cw.Categories.botControl,
        description=f"Cancels the current command. Usually used for `{main.commandPrefix}artistadd`.",
        guildOnly=False
    )
    async def cancel(self, ctx: cmds.Context):
        if isinstance(ctx.channel, discord.DMChannel):
            await sc.ArtistFunctions.deleteIsUsingCommand(sc.ArtistFunctions(), ctx.author.id)
            await ctx.author.send("Command cancelled.")



def setup(bot):
    bot.add_cog(ArtistControl(bot))
