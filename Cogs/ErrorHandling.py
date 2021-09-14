from posix import EX_CANTCREAT
import discord
from discord.ext import commands
import main
from Functions import functionsandstuff as fas
import datetime
import asyncio

commandPrefix = main.commandPrefix

errorPrefix = "**Error!**\n"

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exc):
        if isinstance(exc, commands.CommandOnCooldown):
            time = fas.formatTime(int(str(round(exc.retry_after, 0))[:-2]))

            await fas.sendError(ctx, f"The command is on cooldown for `{time}`` more!")
        elif isinstance(exc, commands.MissingRole):
            await fas.sendError(ctx, f"You don't have the `{exc.missing_role}` role!")
        elif isinstance(exc, commands.MissingRequiredArgument):
            await fas.sendError(ctx, f"Make sure you have the correct parameters! Use `{commandPrefix}help` to get help!")
        elif isinstance(exc, asyncio.exceptions.TimeoutError):
            await fas.sendError(ctx, f"Command timed out. Your original command can be found here: {ctx.message.jump_url}")
        elif isinstance(exc, commands.CommandNotFound):
            return
        else:
            await fas.sendError(ctx, "Something else went wrong. This has been reported.", exc=exc, sendToOwner=True, printToConsole=True)

        

def setup(bot):
    bot.add_cog(ErrorHandler(bot))