"""Artist control."""


import typing as typ

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
