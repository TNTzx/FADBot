# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=no-self-use

from typing import Union
import discord
import discord.ext.commands as cmds

import main
from functions import command_wrapper as c_w
from functions.artist_related import submission as ss
from functions.artist_related import is_using as i_u
from functions.databases.vadb import vadb_interact as v_i
from functions.exceptions import custom_exc as c_exc
from functions.exceptions import send_error as s_e
from functions import other_functions as o_f


class ArtistControl(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot


    # @c_w.command(
    #     category=c_w.Categories.artist_management,
    #     description=f"Requests an artist to be added to the database. Times out after `{o_f.format_time(60 * 2)}``.",
    #     aliases=["aa"],
    #     guild_only=False
    # )
    # async def artistadd(self, ctx: cmds.Context, devbranch=""):
    #     if await i_u.check_if_using_command(ctx.author.id):
    #         await s_e.send_error(ctx, f"You're already using this command! Use {main.CMD_PREFIX}cancel on your DMs with me to cancel the command.")
    #         raise c_exc.ExitFunction("Exited Function.")

    #     await i_u.add_is_using_command(ctx.author.id)

    #     subm = ss.Submission()

    #     if isinstance(ctx.channel, discord.TextChannel):
    #         await ctx.send("The verification submission has been moved to your DMs. Please check it.")

    #     await ctx.author.send("> The verification submission is now being set up. Please __follow the prompts as needed__.")


    #     subm.user.user_id = ctx.author.id

    #     devbranch = devbranch == "devbranch"
    #     if not devbranch:
    #         await subm.set_proof(ctx)
    #         await subm.set_availability(ctx)
    #         await subm.set_name(ctx)
    #         await subm.set_aliases(ctx)
    #         await subm.set_desc(ctx)
    #         await subm.set_avatar(ctx)
    #         await subm.set_banner(ctx)
    #         await subm.set_tracks(ctx)
    #         await subm.set_genre(ctx)
    #         await subm.set_usage_rights(ctx)
    #         await subm.set_socials(ctx)
    #         await subm.set_notes(ctx)


    #     await subm.edit_loop(ctx)

    #     await ctx.send("Submitting...")
    #     await subm.create_vadb_artist()
    #     await ctx.send("The verification form has been submitted. Please wait for the moderators to verify your submission.")

    #     await i_u.delete_is_using_command(ctx.author.id)


    @c_w.command(
        category=c_w.Categories.artist_management,
        description="Gets a specified artist.",
        parameters={
            "[<search term> | <ID>]": "If <search term> is used, then the command will return a list of artists for that search term.\nIf <ID> is used, then the bot will return the artist with that ID."
        },
        aliases=["as"],
        guild_only=False,
        cooldown=5, cooldown_type=cmds.BucketType.user,
        example_usage=[
            "##artistsearch \"Some Random Artist Name\"",
            "##artistsearch 5"
        ]
    )
    async def artistsearch(self, ctx: cmds.Context, term: Union[str, int]):
        try:
            term = int(term)
        except ValueError:
            pass

        if isinstance(term, str):
            artists = v_i.make_request("GET", "/search/{")
        else:
            pass

    @c_w.command(guild_only=False)
    async def testingartist(self, ctx):
        print(ss.Artist().__dict__)



    @c_w.command(
        category=c_w.Categories.bot_control,
        description="Cancels the current command. Usually used for artist commands.",
        guild_only=False
    )
    async def cancel(self, ctx: cmds.Context):
        if isinstance(ctx.channel, discord.DMChannel):
            await i_u.delete_is_using_command(ctx.author.id)
            await ctx.author.send("Command cancelled.")


def setup(bot: cmds.Bot):
    bot.add_cog(ArtistControl(bot))
