"""Artist control."""


import copy

import nextcord as nx
import nextcord.ext.commands as nx_cmds

import backend.vadb_library as vadb
import backend.discord_utils as disc_utils
import backend.exc_utils as exc_utils
import global_vars

from ... import utils as cog


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


class CogArtistCmds(cog.RegisteredCog):
    """Contains artist commands."""


    @disc_utils.command_wrap(
        category = disc_utils.CategoryArtistManagement,
        cmd_info = disc_utils.CmdInfo(
            description = "Creates an `add request`.",
            aliases = ["ara"],
            sustained = True,
            cooldown_info = disc_utils.CooldownInfo(
                length = global_vars.Timeouts.long,
                type_ = nx_cmds.BucketType.user
            ),
            usability_info = disc_utils.UsabilityInfo(
                guild_only = False
            )
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
        cmd_info = disc_utils.CmdInfo(
            description = "Requests an artist to be edited in the database.",
            params = disc_utils.Params(
                disc_utils.ParamArgument(
                    "artist id",
                    description = "The artist's ID to edit."
                )
            ),
            aliases = ["are"],
            sustained = True,
            cooldown_info = disc_utils.CooldownInfo(
                length = global_vars.Timeouts.long,
                type_ = nx_cmds.BucketType.user
            ),
            usability_info = disc_utils.UsabilityInfo(
                guild_only = False
            )
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


    # REWRITE rewrite ##artistverifyadd and ##artistverifyedit
    @disc_utils.command_wrap(
        category = disc_utils.CategoryArtistManagement,
        cmd_info = disc_utils.CmdInfo(
            description = "Accepts / declines the add request.",
            params = disc_utils.Params(
                disc_utils.ParamArgument(
                    "add request id",
                    description = "Add Request ID to verify."
                ),
                disc_utils.ParamsSplit(
                    disc_utils.Params(
                        disc_utils.ParamLiteral(
                            "accept",
                            description = "Accepts the request, adding the artist to the database."
                        )
                    ),
                    disc_utils.Params(
                        disc_utils.ParamLiteral(
                            "decline",
                            description = "Declines the request, discarding it."
                        ),
                        disc_utils.ParamArgument(
                            "reason",
                            description = "The reason for declining the request."
                        )
                    ),
                    description = "Describes the verdict."
                )
            ),
            aliases = ["ava"],
            sustained = True,
            cooldown_info = disc_utils.CooldownInfo(
                length = global_vars.Timeouts.long,
                type_ = nx_cmds.BucketType.user
            ),
            usability_info = disc_utils.UsabilityInfo(
                guild_only = False
            ),
            perms = disc_utils.Permissions([disc_utils.PermPAMod])
        )
    )
    async def artistverifyadd(self, ctx: nx_cmds.Context, add_req_id: int, verdict: str, reason: str = None):
        """Sets the verification status of an `AddRequest`."""
        await ctx.send("Getting request data...")

        try:
            request = vadb.AddRequest.firebase_from_id(add_req_id)
        except vadb.ChangeReqNotFound:
            await exc_utils.SendFailedCmd(
                error_place = exc_utils.ErrorPlace.from_context(ctx),
                suffix = "That `add request` doesn't exist!"
            )


        await ctx.send(f"Are you sure you want to {verdict} this `add request`?")



    # @disc_utils.command(
    #     category = disc_utils.CmdCategories.artist_management,
    #     description = "Accepts / declines the request.",
    #     parameters = {
    #         "[\"add\" / \"edit\"]": "Chooses whether or not the request to be verified is to `add` an artist or `edit` an artist.",
    #         "id": "Artist ID to verify.",
    #         "[\"accept\" / \"decline\"]": "Accepts or declines the verification submission. `accept` to mark the artist as completed, or `decline` to delete the submission.",
    #         "reason": "Reason for declining the verification submission. Only required if you choose `decline`. Surround with quotes."
    #     },
    #     aliases = ["av"],
    #     guild_only = False,
    #     req_pa_mod = True
    # )
    # @i_u.sustained_command()
    # async def artistverify(self, ctx: nx_cmds.Context, _type: str, artist_id: int, action: str, reason: str = None):
    #     await ctx.send("Getting data...")

    #     artist = await a_ch.get_artist_by_id(ctx, artist_id)

    #     if artist.states.status.get_name() != "Pending":
    #         await s_e.send_error(ctx, f"The artist `{artist.name}` is not pending! You must have an artist that is pending!")
    #         return

    #     async def send_logs_and_dms(artist_obj: a_l.Default, logs_message: str, dm_message: str):
    #         await ctx.send(logs_message, embed = await artist_obj.generate_embed())
    #         async def parse_logs(log_list: list[l_l.Log]):
    #             if log_list is None:
    #                 return
    #             if log_list[0].user_id is None:
    #                 return
    #             if len(log_list) == 0:
    #                 return

    #             user_ids = []
    #             for log in log_list:
    #                 if log.user_id not in user_ids:
    #                     user_ids.append(int(log.user_id))

    #             users = [await global_vars.global_bot.fetch_user(user_id) for user_id in user_ids]
    #             for user in users:
    #                 await user.send(dm_message, embed = await artist_obj.generate_embed())

    #             await artist_obj.post_log_to_channels(logs_message, l_l.LogChannelTypes.DUMP.get_all_channels())

    #         await parse_logs(artist_obj.discord_info.logs.pending)
    #         await parse_logs(artist_obj.discord_info.logs.editing)

    #     async def confirm_verify(artist_obj: a_l.Default):
    #         timeout = global_vars.Timeouts.medium

    #         confirm = vw.ViewConfirmCancel()
    #         await ctx.send((
    #             f"Are you sure that you want to `{action}` this `{_type} request`?\n"
    #             f"This command times out in `{o_f.format_time(timeout)}`."
    #         ))
    #         await ctx.send(embed = await artist_obj.generate_embed())
    #         message = await ctx.send(artist_obj.proof, view = confirm)

    #         def check_button(interact: nx.Interaction):
    #             return ctx.author.id == interact.user.id and interact.message.id == message.id

    #         try:
    #             await global_vars.global_bot.wait_for("interaction", check = check_button, timeout = timeout)
    #         except asyncio.TimeoutError:
    #             await s_e.timeout_command(ctx, send_author = True)

    #         if confirm.value == vw.OutputValues.confirm:
    #             return

    #         await s_e.cancel_command(ctx)


    #     def log_verify(artist_obj: a_l.Default):
    #         log_message = (
    #             f"[VERIFY] [{_type.upper()}] [{action.upper()}]: {o_f.pr_print(artist_obj.get_dict())}\n"
    #             f"Reason: {reason}"
    #         )
    #         lgr.log_artist_control.info(log_message)


    #     @c_p.choice_param_cmd(ctx, _type, ["add", "edit"])
    #     async def _type_choice():
    #         if _type == "add":
    #             @c_p.choice_param_cmd(ctx, action, ["accept", "decline"])
    #             async def action_choice():
    #                 await confirm_verify(artist)

    #                 if action == "accept":
    #                     artist.states.status.value = 0

    #                     await ctx.send("Verifying `add request`...")
    #                     a_l.VADB.Send.Edit(artist).send_data(artist.vadb_info.artist_id)
    #                     await send_logs_and_dms(artist, f"The `add request` has been accepted for `{artist.name}`!", f"Your pending `add request` for `{artist.name}` has been accepted!")
    #                 if action == "decline":
    #                     if reason is None:
    #                         await s_e.send_error(ctx, "You didn't provide a reason as to why the `add request` was declined.")
    #                         return
    #                     artist.states.status.value = 1

    #                     await ctx.send("Declining `add request`...")
    #                     a_l.VADB.Send.Delete(artist).send_data()
    #                     await send_logs_and_dms(artist,
    #                         f"The `add request` has been declined for `{artist.name}` due to the following reason: `{reason}`.", (
    #                             f"Your pending `add request` for `{artist.name}` has been denied due to the following reason:\n"
    #                             f"`{reason}`"
    #                         )
    #                     )

    #             await action_choice()

    #             log_verify(artist)

    #             await artist.delete_logs()
    #         elif _type == "edit":
    #             try:
    #                 artist_from_fb = a_l.get_artist_by_id_fb(l_l.LogTypes.EDITING, artist.vadb_info.artist_id)
    #             except c_e.FirebaseNoEntry as exc:
    #                 await s_e.send_error(ctx, "The artist doesn't have a pending edit request!")
    #                 raise c_e.ExitFunction() from exc

    #             @c_p.choice_param_cmd(ctx, action, ["accept", "decline"])
    #             async def action_choice():
    #                 await confirm_verify(artist_from_fb)

    #                 if action == "accept":
    #                     await ctx.send("Verifying `edit request`...")
    #                     artist_from_fb.states.status.value = 0
    #                     a_l.VADB.Send.Edit(artist_from_fb).send_data(artist.vadb_info.artist_id)
    #                     await send_logs_and_dms(artist_from_fb, f"The `edit request` has been accepted for `{artist_from_fb.name}`!", f"Your pending `edit request` for `{artist_from_fb.name}` has been accepted!")
    #                 if action == "decline":
    #                     if reason is None:
    #                         await s_e.send_error(ctx, "You didn't provide a reason as to why the `edit request` was declined.")
    #                         return
    #                     artist.states.status.value = 0
    #                     a_l.VADB.Send.Edit(artist).send_data(artist.vadb_info.artist_id)
    #                     await send_logs_and_dms(artist_from_fb,
    #                         f"The `edit request` has been declined for `{artist_from_fb.name}` due to the following reason: `{reason}`.", (
    #                             f"Your pending `edit request` for `{artist_from_fb.name}` has been denied due to the following reason:\n"
    #                             f"`{reason}`"
    #                         )
    #                     )

    #             await action_choice()

    #             log_verify(artist_from_fb)

    #             await artist_from_fb.delete_logs()

    #     await _type_choice()

    #     await artist.delete_logs()


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


    # @disc_utils.command(
    #     category = disc_utils.CmdCategories.bot_control,
    #     description = "Cancels the current command. Usually used for artist commands.",
    #     guild_only = False
    # )
    # async def cancel(self, ctx: nx_cmds.Context):
    #     if isinstance(ctx.channel, nx.DMChannel):
    #         await i_u.delete_is_using_command(ctx.author.id)
    #         await ctx.author.send("Command cancelled.")
