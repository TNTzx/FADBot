# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=no-self-use

from typing import Union
import discord
import discord.ext.commands as cmds

from global_vars import variables as vrs
from functions import command_wrapper as c_w
from functions.artist_related.artist_classes import artist_data as a_d
from functions.artist_related import is_using as i_u
from functions.databases.vadb import vadb_interact as v_i
from functions.exceptions import custom_exc as c_exc
from functions.exceptions import send_error as s_e
from functions import other_functions as o_f


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
        if await i_u.check_if_using_command(ctx.author.id):
            await s_e.send_error(ctx, self.bot, f"You're already using this command! Use {vrs.CMD_PREFIX}cancel on your DMs with me to cancel the command.")
            raise c_exc.ExitFunction("Exited Function.")

        await i_u.add_is_using_command(ctx.author.id)

        await ctx.send("> The artist verification form is now being set up. Please __follow all instructions as necessary.__")

        data = a_d.Structures.Default()
        if devbranch != "devbranch":
            await data.trigger_all_set_attributes(ctx, self.bot)

        await data.edit_loop(ctx, self.bot)
        response = v_i.make_request("POST", "/artist/", a_d.Structures.VADB.Send.Create(data).get_json_dict())
        v_i.make_request("PATCH", f"/artist/{response['data']['id']}", a_d.Structures.VADB.Send.Edit(data).get_json_dict())

        await ctx.send("The artist verification form has been submitted. Please wait for an official moderator to approve your submission.")

        await i_u.delete_is_using_command(ctx.author.id)


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
        pass
        # try:
        #     term = int(term)
        # except ValueError:
        #     pass

        # if isinstance(term, str):
        #     artists = v_i.make_request("GET", "/search/{")
        # else:
        #     pass


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
