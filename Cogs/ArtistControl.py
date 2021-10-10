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
        if await sc.ArtistFunctions.checkIfUsingCommand(sc.ArtistFunctions(), ctx.author.id):
            await ef.sendError(ctx, f"You're already using this command! Use {main.commandPrefix}cancel on your DMs with me to cancel the command.")
            raise ce.ExitFunction("Exited Function.")

        await sc.ArtistFunctions.addIsUsingCommand(sc.ArtistFunctions(), ctx.author.id)

        subm = sc.Submission()

        await ctx.send("The verification submission has been moved to your DMs. Please check it.")
        await ctx.author.send("> The verification submission is now being set up. Please __follow the prompts as needed__.")

        subm.user.id = ctx.author.id
        await subm.setProof(ctx)
        await subm.setAvailability(ctx)
        await subm.setName(ctx)
        await subm.setAliases(ctx)
        await subm.setDescription(ctx)
        await subm.setAvatar(ctx)
        await subm.setBanner(ctx)
        await subm.setTracks(ctx)
        await subm.setGenre(ctx)
        await subm.setUsageRights(ctx)
        await subm.setSocials(ctx)
        


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
            
            await ctx.author.send(embed=await subm.generateEmbed())
    
            message: discord.Message = await subm.waitFor(ctx)
            command = message.content.split(" ")

            if command[0].startswith(f"{main.commandPrefix}edit"):
                commandToGet = commandDict.get(command[1] if len(command) > 1 else None, None)

                if command == None:
                    await subm.sendError(ctx, f"You didn't specify a valid property! The valid properties are `{'`, `'.join(commandDict.keys())}`")
                
                result = await commandToGet(ctx, skippable=True)
                exec(f"submission{commandToGet['path']} = {result}")
            
            elif command[0] == f"{main.commandPrefix}submit":
                break
                
            elif command[0] == f"{main.commandPrefix}cancel":
                raise ce.ExitFunction("Exited Function.")
            
            else:
                await subm.sendError(ctx, "You didn't send a command!")

        await subm.deleteIsUsingCommand(ctx.author.id)
        


    @cw.command(
        category=cw.Categories.botControl,
        description="Cancels the current command.",
        guildOnly=False
    )
    async def cancel(self, ctx: cmds.Context):
        if isinstance(ctx.channel, discord.DMChannel):
            await sc.ArtistFunctions.deleteIsUsingCommand(sc.ArtistFunctions(), ctx.author.id)
            await ctx.author.send("Command cancelled.")


def setup(bot):
    bot.add_cog(ArtistControl(bot))
