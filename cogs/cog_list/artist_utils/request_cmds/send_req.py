"""Artist control."""


import typing as typ

import copy

import nextcord as nx
import nextcord.ext.commands as nx_cmds

import backend.vadb_library as vadb
import backend.discord_utils as disc_utils
import backend.exc_utils as exc_utils
import global_vars

from .... import utils as cog


async def send_reminder(author: nx.User):
    """Sends the reminder that the VADB site exists."""
    await author.send(
        (
            ">>> Reminder that there is a site for VADB! This bot is built for this site.\n"
            f"Check it out here! {vadb.BASE_LINK}"
        )
    )


async def init_req_cmd(ctx: nx_cmds.Context, req_type: str):
    """Initializes the request command. Returns a tuple. `(Author, DMChannel)`"""
    if not isinstance(ctx.channel, nx.channel.DMChannel):
        await ctx.send(f"The artist {req_type} request form is sent to your DMs. Please check it.")

    author = ctx.author
    dm_channel = author.dm_channel
    if dm_channel is None:
        dm_channel = await author.create_dm()

    await send_reminder(author)
    await dm_channel.send(f"> The artist {req_type} request is now being set up. Please __follow all instructions as necessary.__")

    return author, dm_channel


def get_cmd_info(req_cls: typ.Type[vadb.ChangeRequest], aliases: list[str] = None):
    """Gets the `CmdInfo` from a `ChangeRequest`."""
    return disc_utils.CmdInfo(
        description = f"Creates the `{req_cls.req_type}` request to send over to PA moderators for approval.",
        aliases = aliases,
        sustained = True,
        cooldown_info = disc_utils.CooldownInfo(
            length = global_vars.Timeouts.long,
            type_ = nx_cmds.BucketType.user
        ),
        usability_info = disc_utils.UsabilityInfo(
            guild_only = False
        )
    )


class CogSendeReq(cog.RegisteredCog):
    """Contains commands for making artist requests."""

    @disc_utils.command_wrap(
        category = disc_utils.CategoryArtistManagement,
        cmd_info = get_cmd_info(
            vadb.AddRequest,
            aliases = ["ara"]
        )
    )
    async def artistrequestadd(self, ctx: nx_cmds.Context):
        """Creates an add request."""
        author, dm_channel = await init_req_cmd(ctx, "add")


        form_artist = vadb.disc.FormArtist()

        await author.send("Initiating request editing...")
        await form_artist.edit_with_all_sections(dm_channel, author)

        await author.send("Editing current artist...")
        await form_artist.edit_loop(dm_channel, author)

        add_req = vadb.AddRequest(
            req_info = vadb.ChangeReqInfo(
                user_sender = author,
                artist = form_artist.artist
            )
        )

        await add_req.send_request_pending(dm_channel)


    @disc_utils.command_wrap(
        category = disc_utils.CategoryArtistManagement,
        cmd_info = get_cmd_info(
            vadb.EditRequest,
            aliases = ["ara"]
        )
    )
    async def artistrequestedit(self, ctx: nx_cmds.Context, artist_id: int):
        """Requests an artist to be edited in the database."""
        try:
            current_artist = vadb.Artist.vadb_from_id(artist_id)
        except vadb.VADBNoArtistID:
            await exc_utils.SendFailedCmd(
                error_place = exc_utils.ErrorPlace.from_context(ctx),
                suffix = "There's no artist with that ID!"
            ).send()


        try:
            already_existing_reqs = vadb.EditRequest.firebase_get_all_requests()
        except vadb.ChangeReqNotFound:
            already_existing_reqs = []

        already_existing_req_ids = [request.req_info.artist.vadb_info.artist_id for request in already_existing_reqs]
        if current_artist.vadb_info.artist_id in already_existing_req_ids:
            await exc_utils.SendFailedCmd(
                error_place = exc_utils.ErrorPlace.from_context(ctx),
                suffix = "The artist already has an existing edit request! Please wait until that edit request has been approved or declined!"
            ).send()


        author, dm_channel = await init_req_cmd(ctx, "edit")

        editing_artist = copy.deepcopy(current_artist)

        form_artist = vadb.disc.FormArtist(
            artist = editing_artist
        )

        await form_artist.edit_with_section(
            channel = ctx.channel,
            author = ctx.author,
            section = vadb.disc.FormSections.proof
        )

        while True:
            await form_artist.edit_loop(dm_channel, author)


            await ctx.send("Checking if the artist was edited...")

            duplicate_check_artist = copy.deepcopy(current_artist)
            duplicate_check_artist.proof = editing_artist.proof

            if duplicate_check_artist != editing_artist:
                break

            await exc_utils.SendWarn(
                error_place = exc_utils.ErrorPlace(dm_channel, author),
                suffix = "You didn't edit the artist!",
                try_again = True
            ).send()


        edit_req = vadb.EditRequest(
            req_info = vadb.ChangeReqInfo(
                user_sender = author,
                artist = form_artist.artist
            )
        )

        await edit_req.send_request_pending(dm_channel)
