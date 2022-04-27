"""Contains commands for searching for artists."""


import nextcord.ext.commands as nx_cmds

import backend.discord_utils as disc_utils
import backend.vadb_library as vadb
import backend.exc_utils as exc_utils

from ... import utils as cog


class CogVADBSearch(cog.RegisteredCog):
    """Contains commands for searching for artists and artist requests."""
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
            ),
            usability_info = disc_utils.UsabilityInfo(
                guild_only = False
            )
        )
    )
    async def artistsearch(self, ctx: nx_cmds.Context, term_or_id: str | int):
        """Searches for an artist."""
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


    # TODO add ##artistrequestsearch
    # must include: searching for all artist requests, searching for all requests in a specific type, searching for a request with id or search term
