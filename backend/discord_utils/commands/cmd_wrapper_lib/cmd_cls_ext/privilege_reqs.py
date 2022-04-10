"""Contains logic for checking if a user has enough privilege requirements to use the command."""


import nextcord.ext.commands as nx_cmds

import backend.exc_utils as exc_utils


class CmdPrivilegeReq():
    """Represents a privilege requirement."""
    @classmethod
    def req_check(cls, ctx: nx_cmds.Context):
        """Returns `True` if the privilege requirement has been met."""

    @classmethod
    def req_fail_message(cls):
        """Gets the message for when the requirement has not been met."""

    async def has_met_req(cls, ctx: nx_cmds.Context):
        """Checks if the `Context` meets the current privilege requirements. Sends an error if not met."""
        if not cls.req_check(ctx):
            await exc_utils.send_error(ctx, cls.req_fail_message(), cooldown_reset = True)

# TODO write all privilege reqs
