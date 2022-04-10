"""Contains logic for checking if a user has enough usage requirements to use the command."""


import typing as typ

import backend.firebase as firebase

import nextcord.ext.commands as nx_cmds

import backend.exc_utils as exc_utils

from .. import cmd_wrap_excs


class CmdUsageReq():
    """Represents a usage requirement."""
    @classmethod
    def req_check(cls, ctx: nx_cmds.Context):
        """Returns `True` if the usage requirement has been met for the current `Context`."""

    @classmethod
    def req_fail_message(cls):
        """Gets the message for when the requirement has not been met."""

    @classmethod
    async def discord_has_met_req(cls, ctx: nx_cmds.Context):
        """Checks if the `Context` meets the current usage requirements. Sends an error if not met."""
        if not cls.req_check(ctx):
            await exc_utils.send_error(
                ctx,
                (
                    "You have insufficient permissions!\n"
                    f"{cls.req_fail_message()}"
                ),
                cooldown_reset = True
            )
            raise cmd_wrap_excs.PrivilegeReqNotMet(cls.__name__)

class UsageReqs():
    """Contains a list of enabled usage requirements for this command."""
    def __init__(self, priv_reqs: list[typ.Type[CmdUsageReq]] | None = None):
        self.priv_reqs = priv_reqs


    async def discord_has_met_all_reqs(self, ctx):
        """Checks if the current `Context` meets all usage requirements."""
        for priv_req in self.priv_reqs:
            await priv_req.discord_has_met_req(ctx)


# TODO write all usage reqs
class Dev(CmdUsageReq):
    """Requires the user to be a developer of the bot."""
    @classmethod
    def req_check(cls, ctx: nx_cmds.Context):
        user_id = str(ctx.author.id)
        devs = firebase.get_data(
            firebase.ShortEndpoint.devs.get_path(),
            default = []
        )

        return user_id in devs

    @classmethod
    def req_fail_message(cls):
        return "Only developers of this bot may do this command!"
