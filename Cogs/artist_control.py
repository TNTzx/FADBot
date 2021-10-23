# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument

import discord
import discord.ext.commands as cmds

import main
from functions.exceptions import custom_exc as c_exc
from functions.exceptions import send_error as s_e
from functions import command_wrapper as c_w
from functions import other_functions as o_f
from functions.artist_related import submission as ss


class ArtistControl(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot


    @c_w.command(
        category=c_w.Categories.artist_management,
        description=f"Requests an artist to be added to the database. Times out after `{o_f.format_time(60 * 2)}``.",
        aliases=["aa"],
        guild_only=False
    )
    async def artistadd(self, ctx: cmds.Context, devbranch=""):
        if await ss.ArtistFunctions.check_if_using_command(ss.ArtistFunctions(), ctx.author.id):
            await s_e.send_error(ctx, f"You're already using this command! Use {main.CMD_PREFIX}cancel on your DMs with me to cancel the command.")
            raise c_exc.ExitFunction("Exited Function.")

        await ss.ArtistFunctions.add_is_using_command(ss.ArtistFunctions(), ctx.author.id)

        subm = ss.Submission()

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

        await ss.Submission.delete_is_using_command(ss.Submission(), ctx.author.id)


    @c_w.command(
        category=c_w.Categories.bot_control,
        description=f"Cancels the current command. Usually used for `{main.CMD_PREFIX}artistadd`.",
        guild_only=False
    )
    async def cancel(self, ctx: cmds.Context):
        if isinstance(ctx.channel, discord.DMChannel):
            await ss.ArtistFunctions.delete_is_using_command(ss.ArtistFunctions(), ctx.author.id)
            await ctx.author.send("Command cancelled.")


def setup(bot):
    bot.add_cog(ArtistControl(bot))
