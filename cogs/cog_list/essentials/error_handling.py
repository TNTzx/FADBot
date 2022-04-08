"""Contains error handling."""


import asyncio
import traceback as tr

import nextcord as nx
import nextcord.ext.commands as nx_cmds

import global_vars
import backend.logging.loggers as lgr
import backend.exc_utils.custom_exc as c_e
import backend.exc_utils.send_error as s_e
import backend.other.other_functions as o_f

from ... import utils as cog


CMD_PREFIX = global_vars.CMD_PREFIX

class CogErrorHandler(cog.RegisteredCog):
    """Contains error handling."""

    @nx_cmds.Cog.listener()
    async def on_command_error(self, ctx: nx_cmds.Context, exc: Exception | nx_cmds.CommandInvokeError):
        def checkexc(exc_type):
            return isinstance(exc, exc_type)

        if checkexc(nx_cmds.CommandOnCooldown):
            time = o_f.format_time(int(str(round(exc.retry_after, 0))[:-2]))
            await s_e.send_error(ctx, f"The command is on cooldown for `{time}` more!")
            return

        if checkexc(nx_cmds.MissingRole):
            await s_e.send_error(ctx, f"You don't have the `{exc.missing_role}` role!", cooldown_reset = True)
            return

        if checkexc(nx_cmds.MissingRequiredArgument) or checkexc(nx_cmds.BadArgument):
            await s_e.send_error(ctx, f"Make sure you have the correct parameters! Use `{CMD_PREFIX}help` to get help!", cooldown_reset = True)
            return

        if checkexc(nx_cmds.ExpectedClosingQuoteError) or checkexc(nx_cmds.InvalidEndOfQuotedStringError) or checkexc(nx_cmds.UnexpectedQuoteError):
            await s_e.send_error(ctx, "Your quotation marks (`\"`) are wrong! Double-check the command if you have missing quotation marks!", cooldown_reset = True)
            return

        if checkexc(nx_cmds.MissingRequiredArgument):
            await s_e.send_error(ctx, f"Make sure you have the correct parameters! Use `{global_vars.CMD_PREFIX}help` to get help!")
            return

        if checkexc(nx_cmds.NoPrivateMessage):
            await s_e.send_error(ctx, "This command is disabled in DMs!", cooldown_reset = True)
            return

        if checkexc(nx_cmds.CommandInvokeError):
            if isinstance(exc.original, c_e.ExitFunction):
                return

            if hasattr(exc.original, "status"):
                if exc.original.status == 403:
                    error_message = f"Forbidden from sending. Code {exc.original.code}: {exc.original.text}"
                    lgr.log_discord_forbidden.warning(error_message)
                    return

            if isinstance(exc.original, asyncio.TimeoutError):
                await s_e.send_error(ctx, "Command timed out. Please run the command again.")
                return

            if isinstance(exc.original, nx.NotFound):
                error_message = f"Not found. Code {exc.original.code}: {exc.original.text}"
                lgr.log_discord_forbidden.warning(error_message)
                return

        if checkexc(nx_cmds.CommandNotFound):
            return

        lgr.log_global_exc.error("".join(tr.format_exception(exc.original)))
        await s_e.send_error(ctx, "Something went wrong. This error has been reported to the owner of the bot.", exc = exc, send_owner = True, send_console = True)
