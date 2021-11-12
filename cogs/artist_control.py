# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=no-self-use

from typing import Union
import discord
import discord.ext.commands as cmds
import requests as req

from global_vars import variables as vrs
from functions import command_wrapper as c_w
from functions.artist_related.classes import artist_library as a_l
from functions.artist_related import is_using as i_u
from functions.exceptions import send_error as s_e
from functions import other_functions as o_f


class ArtistControl(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot


    @c_w.command(
        category=c_w.Categories.artist_management,
        description=f"Requests an artist to be added to the database. Times out after `{o_f.format_time(60 * 2)}`.",
        aliases=["aa"],
        guild_only=False
    )
    async def artistadd(self, ctx: cmds.Context, devbranch=""):
        if await i_u.check_if_using_command(ctx.author.id):
            await s_e.send_error(ctx, self.bot, f"You're already using this command! Use {vrs.CMD_PREFIX}cancel on your DMs with me to cancel the command.")
            return

        await i_u.add_is_using_command(ctx.author.id)

        if not isinstance(ctx.channel, discord.channel.DMChannel):
            await ctx.send("The form is being set up on your DMs. Please check it.")

        await ctx.author.send("> The artist verification form is now being set up. Please __follow all instructions as necessary.__")

        data = a_l.Structures.Default()
        if devbranch != "devbranch":
            await data.trigger_all_set_attributes(ctx, self.bot)

        await data.edit_loop(ctx, self.bot)

        response = a_l.Structures.VADB.Send.Create(data).send_data()

        artist_id = response["data"]["id"]
        a_l.Structures.VADB.Send.Edit(data).send_data(artist_id)
        data.vadb_info.artist_id = artist_id

        await ctx.author.send("The artist verification form has been submitted. Please wait for an official moderator to approve your submission.")
        await i_u.delete_is_using_command(ctx.author.id)

        await data.post_log(self.bot)
        a_l.Structures.Firebase.Pending(data).send_data()


    @c_w.command(
        category=c_w.Categories.artist_management,
        description="Accepts / declines the verification submission.",
        parameters={
            "[accept / decline]": "Accepts or declines the verification submission. `accept` to mark the artist as completed, or `decline` to delete the submission.",
            "id": "Artist ID to verify."
        },
        aliases=["av"],
        guild_only=False,
        req_pa_mod=True
    )
    async def artistverify(self, ctx: cmds.Context, artist_id: int, action: str):
        try:
            artist: a_l.Structures.Default = a_l.get_artist_by_id(artist_id)
        except req.exceptions.HTTPError:
            await s_e.send_error(ctx, self.bot, "The artist doesn't exist. Try again?")
            return

        if artist.states.status.value != 2:
            await s_e.send_error(ctx, self.bot, f"The artist `{artist.name}` is not pending! You must have an artist that is pending!")
            return

        action = action.lower()
        if action not in ("accept", "decline"):
            await s_e.send_error(ctx, self.bot, f"Make sure you have the correct parameters! `{action}` is not a valid parameter.")
            return


        if action == "accept":
            artist.states.status.value = 0
            a_l.Structures.VADB.Send.Edit(artist).send_data(artist.vadb_info.artist_id)
            await ctx.send(f"Success! The verification submission is now complete for `{artist.name}`!")
        if action == "decline":
            a_l.Structures.VADB.Send.Delete(artist).send_data()
            await ctx.send(f"Success! The verification submission is now deleted for `{artist.name}`!")


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
        search_result = a_l.search_for_artist(term)
        try:
            term = int(term)
        except (ValueError, TypeError):
            pass

        if isinstance(term, int):
            try:
                artist: a_l.Structures.Default = a_l.get_artist_by_id(term)
                await ctx.send(embed=await artist.generate_embed())
            except req.exceptions.HTTPError:
                await s_e.send_error(ctx, self.bot, "The artist doesn't exist. Try again?")
            return

        if search_result is None:
            await s_e.send_error(ctx, self.bot, "Your search term has no results. The artist might also be pending, in which case you can try `##artistsearch <id>` instead. Try again?")
            return

        if len(search_result) == 1:
            await ctx.send(embed=await search_result[0].generate_embed())
        elif len(search_result) > 1:
            await ctx.send("Multiple artists found! Use `##artistsearch <id>` to search for a specific artist.", embed=a_l.generate_search_embed(search_result))


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
