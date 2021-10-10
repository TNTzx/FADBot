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
from Functions.ArtistManagement.SubmissionClass import Submission
from Functions.ArtistManagement import ArtistControlFunctions as acf
from Functions.ArtistManagement import ArtistDataFormat as adf


class ArtistControl(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot  


    @cw.command(
        category=cw.Categories.artistManagement,
        description=f"Requests an artist to be added to the database. Times out after `{ef.formatTime(60 * 2)}``.",
        aliases=["aa"]
    )
    async def artistadd(self, ctx: cmds.Context):
        if await acf.checkIfUsingCommand(ctx.author.id):
            await ef.sendError(ctx, f"You're already using this command! Use {main.commandPrefix}cancel on your DMs with me to cancel the command.")
            raise ce.ExitFunction("Exited Function.")

        await acf.addIsUsingCommand(ctx.author.id)

        subm = Submission()

        await ctx.send("The verification submission has been moved to your DMs. Please check it.")
        await ctx.author.send("> The verification submission is now being set up. Please __follow the prompts as needed__.")

        subm.user.id = ctx.author.id
        subm.setProof(ctx)
        subm.setAvailability(ctx)
        subm.setName(ctx)
        subm.setAliases(ctx)
        subm.setDescription(ctx)
        subm.setAvatar(ctx)
        subm.setBanner(ctx)
        subm.setTracks(ctx)
        subm.setGenre(ctx)
        subm.setUsageRights(ctx)
        subm.setSocials(ctx)
        
        submission = {'userInfo': {'id': 279803094722674693}, 'artistInfo': {'proof': 'https://cdn.discordapp.com/attachments/890222271849963571/895946184135434240/unknown.png', 'vadbpage': 'https://fadb.live/', 'data': {'id': None, 'name': 'text', 'aliases': [{'name': 'alias'}, {'name': 
'alias'}], 'avatar': 'https://cdn.discordapp.com/attachments/890222271849963571/895946400515371038/2Pp9omj.png', 'banner': 'https://cdn.discordapp.com/attachments/890222271849963571/895946423558869043/beahjksd.png', 'description': 'aaaaaaaaaaa', 'tracks': 
123, 'genre': 'q', 'status': 0, 'availability': 0, 'notes': 'text', 'usageRights': [{'name': 'All songs', 'value': True}, {'name': 'q', 'value': False}], 'socials': [{'url': 'https://stackoverflow.com/questions/1186789/what-is-the-best-way-to-call-a-script-from-another-script', 'type': 'Stackoverflow'}]}}}

        commandDict = {
            "proof": subm.setProof,
            "availability": subm.setAvailability,
            "name": subm.setName,
            "aliases": subm.setAliases,
            "description": subm.setDescription,
            "avatar": subm.setAvatar,
            "banner": subm.setBanner,
            "tracks": subm.setTracks,
            "genre": subm.setGenre,
            "usagerights": subm.setUsageRights,
            "socials": subm.setSocials
        }

        while True:
            await ctx.author.send(f"This is the generated artist profile.\nUse `{main.commandPrefix}edit <property>` to edit a property, `{main.commandPrefix}submit` to submit this verification for approval, or `{main.commandPrefix}cancel` to cancel this command.")
            
            await ctx.author.send(embed=await acf.generateEmbed(submission))
    
            message: discord.Message = await acf.waitFor(ctx)
            command = message.content.split(" ")

            if command[0].startswith(f"{main.commandPrefix}edit"):
                commandToGet = commandDict.get(command[1] if len(command) > 1 else None, None)

                if command == None:
                    await acf.sendError(ctx, f"You didn't specify a valid property! The valid properties are `{'`, `'.join(commandDict.keys())}`")
                
                result = await commandToGet(ctx, skippable=True)
                exec(f"submission{commandToGet['path']} = {result}")
            
            elif command[0] == f"{main.commandPrefix}submit":
                break
                
            elif command[0] == f"{main.commandPrefix}cancel":
                raise ce.ExitFunction("Exited Function.")
            
            else:
                await acf.sendError(ctx, "You didn't send a command!")

        await acf.deleteIsUsingCommand(ctx.author.id)
        


    @cw.command(
        category=cw.Categories.botControl,
        description="Cancels the current command.",
        guildOnly=False
    )
    async def cancel(self, ctx: cmds.Context):
        if isinstance(ctx.channel, discord.DMChannel):
            await acf.deleteIsUsingCommand(ctx.author.id)
            await ctx.author.send("Command cancelled.")


def setup(bot):
    bot.add_cog(ArtistControl(bot))
