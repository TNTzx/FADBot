# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument

# import discord
from discord.ext import commands

import main
from Functions import ExtraFunctions as ef
from Functions.ArtistManagement import SubmissionClass as sc

CMD_PREFIX = main.CMD_PREFIX

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exc):
        def checkexc(exc_type):
            return isinstance(exc, exc_type)

        if checkexc(commands.CommandOnCooldown):
            time = ef.format_time(int(str(round(exc.retry_after, 0))[:-2]))
            await ef.send_error(ctx, f"The command is on cooldown for `{time}`` more!", cooldown_reset=True)
            return

        elif checkexc(commands.MissingRole):
            await ef.send_error(ctx, f"You don't have the `{exc.missing_role}` role!", cooldown_reset=True)
            return

        elif checkexc(commands.MissingRequiredArgument):
            await ef.send_error(ctx, f"Make sure you have the correct parameters! Use `{CMD_PREFIX}help` to get help!", cooldown_reset=True)
            return

        elif checkexc(commands.ExpectedClosingQuoteError) or checkexc(commands.InvalidEndOfQuotedStringError) or checkexc(commands.UnexpectedQuoteError):
            await ef.send_error(ctx, "Your quotation marks (`\"`) are wrong! Double-check the command if you have missing quotation marks!", cooldown_reset=True)
            return

        elif checkexc(commands.MissingRequiredArgument):
            await ef.send_error(ctx, f"Make sure you have the correct parameters! Use `{main.CMD_PREFIX}help` to get help!")
            return

        elif checkexc(commands.NoPrivateMessage):
            await ef.send_error(ctx, "This command is disabled in DMs!", cooldown_reset=True)
            return

        elif checkexc(commands.CommandInvokeError):
            if str(exc.__cause__) == "Exited Function.":
                return

        elif checkexc(commands.CommandNotFound):
            return

        await sc.ArtistFunctions.delete_is_using_command(sc.ArtistFunctions(), ctx.author.id)
        await ef.send_error(ctx, "Something went wrong. This error has been reported to the owner of the bot.", exc=exc, send_owner=True, send_console=True)



def setup(bot):
    bot.add_cog(ErrorHandler(bot))
