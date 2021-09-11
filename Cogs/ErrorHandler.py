import discord
from discord.ext import commands
import os
import asyncio

from discord.ext.commands.errors import CommandNotFound
import main
import sys
import traceback
import datetime

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exc):

        if isinstance(exc, commands.CommandOnCooldown):
            await ctx.send(f"Error! \n The command is on cooldown for {str(round(exc.retry_after, 0))[:-2]} seconds more!")
            return
        elif isinstance(exc, commands.CommandNotFound):
            return

        error = getattr(exc, 'original', exc)

        print(f"Ignoring exception in command {ctx.command}:")
        traceback.print_exception(type(error), error, error.__traceback__)

        await ctx.send(f"Error! ```{error}```")

def setup(bot):
    bot.add_cog(ErrorHandler(bot))