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

        def checkexc(type):
            return isinstance(exc, type)
    
        if checkexc(commands.CommandOnCooldown):
            time = fas.formatTime(int(str(round(exc.retry_after, 0))[:-2]))

            await fas.sendError(ctx, f"The command is on cooldown for `{time}`` more!")

        elif checkexc(commands.MissingRole):
            await fas.sendError(ctx, f"You don't have the `{exc.missing_role}` role!")
    
        elif checkexc(commands.MissingRequiredArgument):
            await fas.sendError(ctx, f"Make sure you have the correct parameters! Use `{commandPrefix}help` to get help!")
        
        elif checkexc(commands.CommandNotFound):
            return

        else:
            await fas.sendError(ctx, "Something went wrong. This error has been reported to the owner of the bot.", exc=exc, sendToOwner=True, printToConsole=True)

        

def setup(bot):
    bot.add_cog(ErrorHandler(bot))