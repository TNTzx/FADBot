"""Artist control."""


import typing as typ

import nextcord as nx
import nextcord.ext.commands as nx_cmds

import backend.vadb_library as vadb
import backend.discord_utils as disc_utils
import backend.exc_utils as exc_utils
import global_vars

from .... import utils as cog


async def artist_verify(ctx: nx_cmds.Context, req_cls: typ.Type[vadb.ChangeRequest], req_id: int, verdict: str, reason: str = None):
    """Verifies the artist."""
    @disc_utils.choice_param_cmd(ctx, verdict, ["accept", "decline"])
    async def get_verdict_bool():
        return verdict == "accept"

    verdict_bool = await get_verdict_bool()


    if (not verdict_bool) and (reason is None):
        await exc_utils.SendFailedCmd(
            error_place = exc_utils.ErrorPlace.from_context(ctx),
            suffix = "You didn't provide a reason! Reasons must be provided when you are denying a request!"
        ).send()


    await ctx.send(f"Getting `{req_cls.req_type}` request data...")

    try:
        request = req_cls.firebase_from_id(req_id)
    except vadb.ChangeReqNotFound:
        await exc_utils.SendFailedCmd(
            error_place = exc_utils.ErrorPlace.from_context(ctx),
            suffix = f"That `{req_cls.req_type}` request doesn't exist!"
        ).send()


    try:
        await request.set_approval(
            channel = ctx.channel,
            author = ctx.author,
            is_approved = verdict_bool,
            reason = reason
        )
    except vadb.SetApprovalCancelled:
        await exc_utils.SendCancel(error_place = exc_utils.ErrorPlace.from_context(ctx)).send()


def get_params(req_cls: typ.Type[vadb.ChangeRequest]):
    """Gets the parameters for the verify command."""
    return disc_utils.Params(
        disc_utils.ParamArgument(
            f"{req_cls.req_type} request id",
            description = f"{req_cls.req_type.capitalize()} Request ID to verify."
        ),
        disc_utils.ParamsSplit(
            disc_utils.Params(
                disc_utils.ParamLiteral(
                    "accept",
                    description = f"Accepts the {req_cls.req_type} request."
                )
            ),
            disc_utils.Params(
                disc_utils.ParamLiteral(
                    "decline",
                    description = f"Declines the {req_cls.req_type} request, discarding it."
                ),
                disc_utils.ParamArgument(
                    "reason",
                    description = f"The reason for declining the {req_cls.req_type} request."
                )
            ),
            description = "Describes the verdict."
        )
    )


def get_cmd_info(req_cls: typ.Type[vadb.ChangeRequest], aliases: list[str] = None):
    """Gets the `CmdInfo` from the `ChangeRequest`."""
    return disc_utils.CmdInfo(
        description = f"Accepts / declines the {req_cls} request.",
        params = get_params(req_cls),
        aliases = aliases,
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


class CogVerifyReq(cog.RegisteredCog):
    """Contains commands for verifying artist requests."""

    @disc_utils.command_wrap(
        category = disc_utils.CategoryArtistManagement,
        cmd_info = get_cmd_info(
            vadb.AddRequest,
            aliases = ["ava"]
        )
    )
    async def artistverifyadd(self, ctx: nx_cmds.Context, req_id: int, verdict: str, reason: str = None):
        """Sets the verification status of an `AddRequest`."""
        await artist_verify(
            ctx = ctx,
            req_cls = vadb.AddRequest,
            req_id = req_id,
            verdict = verdict,
            reason = reason
        )


    # REWRITE artistverifyedit
    @disc_utils.command_wrap(
        category = disc_utils.CategoryArtistManagement,
        cmd_info = get_cmd_info(
            vadb.EditRequest,
            aliases = ["ave"]
        )
    )
    async def artistverifyedit(self, ctx: nx_cmds.Context, req_id: int, verdict: str, reason: str = None):
        """Sets the verification status of an `EditRequest`."""
        await artist_verify(
            ctx = ctx,
            req_cls = vadb.EditRequest,
            req_id = req_id,
            verdict = verdict,
            reason = reason
        )


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
