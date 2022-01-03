# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=no-self-use

import asyncio
import traceback as tr
import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import global_vars.loggers as lgr
import backend.exceptions.custom_exc as c_e
import backend.exceptions.send_error as s_e
import backend.other_functions as o_f


CMD_PREFIX = vrs.CMD_PREFIX

class ErrorHandler(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cmds.Cog.listener()
    async def on_command_error(self, ctx: cmds.Context, exc: Exception | cmds.CommandInvokeError):
        def checkexc(exc_type):
            return isinstance(exc, exc_type)

        if checkexc(cmds.CommandOnCooldown):
            time = o_f.format_time(int(str(round(exc.retry_after, 0))[:-2]))
            await s_e.send_error(ctx, f"The command is on cooldown for `{time}` more!")
            return

        if checkexc(cmds.MissingRole):
            await s_e.send_error(ctx, f"You don't have the `{exc.missing_role}` role!", cooldown_reset=True)
            return

        if checkexc(cmds.MissingRequiredArgument) or checkexc(cmds.BadArgument):
            await s_e.send_error(ctx, f"Make sure you have the correct parameters! Use `{CMD_PREFIX}help` to get help!", cooldown_reset=True)
            return

        if checkexc(cmds.ExpectedClosingQuoteError) or checkexc(cmds.InvalidEndOfQuotedStringError) or checkexc(cmds.UnexpectedQuoteError):
            await s_e.send_error(ctx, "Your quotation marks (`\"`) are wrong! Double-check the command if you have missing quotation marks!", cooldown_reset=True)
            return

        if checkexc(cmds.MissingRequiredArgument):
            await s_e.send_error(ctx, f"Make sure you have the correct parameters! Use `{vrs.CMD_PREFIX}help` to get help!")
            return

        if checkexc(cmds.NoPrivateMessage):
            await s_e.send_error(ctx, "This command is disabled in DMs!", cooldown_reset=True)
            return

        if checkexc(cmds.CommandInvokeError):
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

        if checkexc(cmds.CommandNotFound):
            return

        lgr.log_global_exc.error("".join(tr.format_exception(exc.original)))
        await s_e.send_error(ctx, "Something went wrong. This error has been reported to the owner of the bot.", exc=exc, send_owner=True, send_console=True)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
