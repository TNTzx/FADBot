# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument

import discord
import discord.ext.commands as cmds

import main
from Functions import CustomExceptions as ce
from Functions import CommandWrappingFunction as cw
from Functions import ExtraFunctions as ef
from Functions.ArtistManagement import SubmissionClass as sc


class ArtistControl(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot


    @cw.command(
        category=cw.Categories.artist_management,
        description=f"Requests an artist to be added to the database. Times out after `{ef.format_time(60 * 2)}``.",
        aliases=["aa"],
        guild_only=False
    )
    async def artistadd(self, ctx: cmds.Context, devbranch=""):
        if await sc.ArtistFunctions.check_if_using_command(sc.ArtistFunctions(), ctx.author.id):
            await ef.send_error(ctx, f"You're already using this command! Use {main.CMD_PREFIX}cancel on your DMs with me to cancel the command.")
            raise ce.ExitFunction("Exited Function.")

        await sc.ArtistFunctions.add_is_using_command(sc.ArtistFunctions(), ctx.author.id)

        subm = sc.Submission()

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send("The verification submission has been moved to your DMs. Please check it.")

        await ctx.author.send("> The verification submission is now being set up. Please __follow the prompts as needed__.")


        subm.user.user_id = ctx.author.id

        devbranch = devbranch == "devbranch"
        if not devbranch:
            await subm.set_proof(ctx)
            await subm.set_availability(ctx)
            await subm.set_name(ctx)
            await subm.set_aliases(ctx)
            await subm.set_desc(ctx)
            await subm.set_avatar(ctx)
            await subm.set_banner(ctx)
            await subm.set_tracks(ctx)
            await subm.set_genre(ctx)
            await subm.set_usage_rights(ctx)
            await subm.set_socials(ctx)
            await subm.set_notes(ctx)
            

        await subm.edit_loop(ctx)

        await ctx.send("Submitting...")
        await subm.create_vadb_artist()
        await ctx.send("The verification form has been submitted. Please wait for the moderators to verify your submission.")

        await sc.Submission.delete_is_using_command(sc.Submission(), ctx.author.id)


    @cw.command(
        category=cw.Categories.bot_control,
        description=f"Cancels the current command. Usually used for `{main.CMD_PREFIX}artistadd`.",
        guild_only=False
    )
    async def cancel(self, ctx: cmds.Context):
        if isinstance(ctx.channel, discord.DMChannel):
            await sc.ArtistFunctions.delete_is_using_command(sc.ArtistFunctions(), ctx.author.id)
            await ctx.author.send("Command cancelled.")


def setup(bot):
    bot.add_cog(ArtistControl(bot))
