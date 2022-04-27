"""Contains commands for searching for artists."""


import nextcord as nx
import nextcord.ext.commands as nx_cmds

import backend.discord_utils as disc_utils
import backend.vadb_library as vadb
import backend.exc_utils as exc_utils

from ... import utils as cog


class CogVerifyReq(cog.RegisteredCog):
    """Contains commands for verifying artist requests."""
    @disc_utils.command_wrap(
        category = disc_utils.CategoryArtistManagement,
        cmd_info = disc_utils.CmdInfo(
            description = "Displays a speficied artist by search term or ID.",
            params = disc_utils.Params(
                disc_utils.ParamsSplit(
                    disc_utils.Params(
                        disc_utils.ParamArgument(
                            "artist id",
                            description = "The artist ID."
                        )
                    ),
                    disc_utils.Params(
                        disc_utils.ParamArgument(
                            "search term",
                            description = "The search term. If multiple artists are found with the search term, the bot will warn."
                        )
                    ),
                    description = "Choose between searching by ID or by search term."
                )
            ),
            aliases = ["as"],
            sustained = True,
            cooldown_info = disc_utils.CooldownInfo(
                length = 5,
                type_ = nx_cmds.BucketType.user
            )
        )
    )
    async def artistsearch(self, ctx: nx_cmds.Context, term_or_id: str | int):
        try:
            term_or_id = int(term_or_id)
        except (ValueError, TypeError):
            pass

        await ctx.send("Searching for artist...")

        if isinstance(term_or_id, int):
            try:
                selected_artist = vadb.Artist.vadb_from_id(term_or_id)
            except vadb.VADBNoArtistID:
                await exc_utils.SendFailedCmd(
                    error_place = exc_utils.ErrorPlace.from_context(ctx),
                    suffix = "There's no artist with that ID!"
                ).send()
                return
        elif isinstance(term_or_id, str):
            try:
                artist_query = vadb.ArtistQuery.from_search(term_or_id)
            except vadb.VADBNoSearchResult:
                await exc_utils.SendFailedCmd(
                    error_place = exc_utils.ErrorPlace.from_context(ctx),
                    suffix = "No artist found with that search term!"
                ).send()
                return

            if len(artist_query.query_items) > 1:
                await ctx.send(embed = artist_query.generate_embed())
                return

            selected_artist = artist_query.query_items[0]


        await ctx.send(embed = vadb.disc.InfoBundle(selected_artist).get_embed())


    # @disc_utils.command(
    #     category = disc_utils.CmdCategories.artist_management,
    #     description = "Gets a specified artist by search term or VADB ID.",
    #     parameters = {
    #         "[<search term> | <ID>]": (
    #             "If <search term> is used, then the command will return a list of artists for that search term.\n"
    #             "If <ID> is used, then the bot will return the artist with that ID."
    #         )
    #     },
    #     aliases = ["as"],
    #     guild_only = False,
    #     cooldown = 5, cooldown_type = nx_cmds.BucketType.user,
    #     example_usage = [
    #         "##artistsearch \"Some Random Artist Name\"",
    #         "##artistsearch 5"
    #     ]
    # )
    # async def artistsearch(self, ctx: nx_cmds.Context, term: str | int):
    #     try:
    #         term = int(term)
    #     except (ValueError, TypeError):
    #         pass

    #     await ctx.send("Searching for artist...")

    #     if isinstance(term, int):
    #         artist = await a_ch.get_artist_by_id(ctx, term)
    #         await ctx.send(embed = await artist.generate_embed())
    #         return

    #     search_result = a_l.search_for_artist(term)
    #     if search_result is None:
    #         await s_e.send_error(ctx, "Your search term has no results. The artist might also be pending, in which case you can try `##artistsearch <id>` instead. Try again?")
    #         return

    #     if len(search_result) == 1:
    #         await ctx.send(embed = await search_result[0].generate_embed())
    #     elif len(search_result) > 1:
    #         await ctx.send("Multiple artists found! Use `##artistsearch <id>` to search for a specific artist.", embed = a_l.generate_search_embed(search_result))


