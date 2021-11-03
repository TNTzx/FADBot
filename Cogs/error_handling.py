# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=no-self-use

# import discord
import discord.ext.commands as cmds

from global_vars import variables as vrs
from functions import other_functions as o_f
from functions.exceptions import send_error as s_e
from functions.artist_related import is_using as i_u

CMD_PREFIX = vrs.CMD_PREFIX

class ErrorHandler(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cmds.Cog.listener()
    async def on_command_error(self, ctx: cmds.Context, exc: Exception):
        def checkexc(exc_type):
            return isinstance(exc, exc_type)

        if checkexc(cmds.CommandOnCooldown):
            time = o_f.format_time(int(str(round(exc.retry_after, 0))[:-2]))
            await s_e.send_error(ctx, self.bot, f"The command is on cooldown for `{time}` more!", cooldown_reset=True)
            return

        elif checkexc(cmds.MissingRole):
            await s_e.send_error(ctx, self.bot, f"You don't have the `{exc.missing_role}` role!", cooldown_reset=True)
            return

        elif checkexc(cmds.MissingRequiredArgument):
            await s_e.send_error(ctx, self.bot, f"Make sure you have the correct parameters! Use `{CMD_PREFIX}help` to get help!", cooldown_reset=True)
            return

        elif checkexc(cmds.ExpectedClosingQuoteError) or checkexc(cmds.InvalidEndOfQuotedStringError) or checkexc(cmds.UnexpectedQuoteError):
            await s_e.send_error(ctx, self.bot, "Your quotation marks (`\"`) are wrong! Double-check the command if you have missing quotation marks!", cooldown_reset=True)
            return

        elif checkexc(cmds.MissingRequiredArgument):
            await s_e.send_error(ctx, self.bot, f"Make sure you have the correct parameters! Use `{vrs.CMD_PREFIX}help` to get help!")
            return

        elif checkexc(cmds.NoPrivateMessage):
            await s_e.send_error(ctx, self.bot, "This command is disabled in DMs!", cooldown_reset=True)
            return

        elif checkexc(cmds.CommandInvokeError):
            if str(exc.__cause__) == "Exited Function.":
                return

        elif checkexc(cmds.CommandNotFound):
            return

        await i_u.delete_is_using_command(ctx.author.id)
        await s_e.send_error(ctx, self.bot, "Something went wrong. This error has been reported to the owner of the bot.", exc=exc, send_owner=True, send_console=True)



def setup(bot):
    bot.add_cog(ErrorHandler(bot))
