"""Contains logic for checking if a user has enough privilege requirements to use the command."""


import nextcord.ext.commands as nx_cmds

import backend.exc_utils as exc_utils

from .. import cmd_wrap_excs


class CmdPrivilegeReq():
    """Represents a privilege requirement."""
    @classmethod
    def req_check(cls, ctx: nx_cmds.Context):
        """Returns `True` if the privilege requirement has been met for the current `Context`."""

    @classmethod
    def req_fail_message(cls):
        """Gets the message for when the requirement has not been met."""

    async def discord_has_met_req(cls, ctx: nx_cmds.Context):
        """Checks if the `Context` meets the current privilege requirements. Sends an error if not met."""
        if not cls.req_check(ctx):
            await exc_utils.send_error(ctx, cls.req_fail_message(), cooldown_reset = True)
            raise cmd_wrap_excs.PrivilegeReqNotMet(cls.__name__)


class PrivilegeReqs():
    """Contains a list of enabled privilege requirements."""
    def __init__(self, priv_reqs: list[CmdPrivilegeReq] | None = None):
        self.priv_reqs = priv_reqs


    async def discord_has_met_all_reqs(self, ctx):
        """Checks if the current `Context` meets all privilege requirements."""
        for priv_req in self.priv_reqs:
            await priv_req.discord_has_met_req(ctx)

# TODO write all privilege reqs
