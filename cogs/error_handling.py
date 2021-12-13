# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=no-self-use

# import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import functions.other_functions as o_f
import functions.exceptions.send_error as s_e


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
            await s_e.send_error(ctx, f"The command is on cooldown for `{time}` more!", cooldown_reset=False)
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
            if str(exc.__cause__) == "Exited Function.":
                return
            if hasattr(exc.original, "status"): 
                if exc.original.status == 403:
                    print(f"Forbidden. Code {exc.original.code}: {exc.original.text}")
                    return

        if checkexc(cmds.CommandNotFound):
            return

        await s_e.send_error(ctx, "Something went wrong. This error has been reported to the owner of the bot.", exc=exc, send_owner=True, send_console=True)



def setup(bot):
    bot.add_cog(ErrorHandler(bot))
