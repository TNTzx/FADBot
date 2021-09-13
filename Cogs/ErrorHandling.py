from discord.ext import commands
import main
from Functions import functionsandstuff as fas
import datetime

commandPrefix = main.commandPrefix

errorPrefix = "**Error!**\n"

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exc):
        if isinstance(exc, commands.CommandOnCooldown):
            numberOfSeconds = int(str(round(exc.retry_after, 0))[:-2])
            timeConverted = str(datetime.timedelta(seconds=numberOfSeconds))
            timeSplit = timeConverted.split(":")
            timeFormatted = f"`{timeSplit[0]}h {timeSplit[1]}m {timeSplit[2]}s`"

            await fas.sendError(ctx, f"The command is on cooldown for `{timeFormatted}`` more!")
        elif isinstance(exc, commands.MissingRole):
            await fas.sendError(ctx, f"You don't have the `{exc.missing_role}` role!")
        elif isinstance(exc, commands.MissingRequiredArgument):
            await fas.sendError(ctx, f"Make sure you have the correct parameters! Use `{commandPrefix}help` to get help!")
        elif isinstance(exc, commands.CommandNotFound):
            return
        else:
            await fas.sendError(ctx, "Something else went wrong. This has been reported.", exc=exc, sendToOwner=True, printToConsole=True)

        

def setup(bot):
    bot.add_cog(ErrorHandler(bot))