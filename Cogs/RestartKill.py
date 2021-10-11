import discord
import discord.ext.commands as cmds
import os, sys

import main
from Functions import CommandWrappingFunction as cw

class RestartKill(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @cw.command(
        category=cw.Categories.botControl,
        description="Restarts the bot.",
        aliases=["sr"],
        requireDev=True
    )
    async def switchrestart(self, ctx):
        await ctx.send("Restarting bot...")
        main.restartBot()
        await ctx.send("Restarted!")
        print("\n \n Restart break! -------------------------------------- \n \n")


    @cw.command(
        category=cw.Categories.botControl,
        description="Shuts down the bot.",
        aliases=["sk"],
        requireDev=True
    )
    async def switchkill(self, ctx):
        await ctx.send("Terminated bot.")
        await main.bot.logout()


    @cw.command(
        category=cw.Categories.botControl,
        description=f"Like {main.commandPrefix}restart, but hard.",
        aliases=["srh"],
        requireDev=True
    )
    async def switchrestarthard(self, ctx):
        await ctx.send("Restart initiated!")
        print("\n \n Restart break! Hard! -------------------------------------- \n \n")
        args = ['python'] + [f"\"{sys.argv[0]}\""]
        os.execv(sys.executable, args)


    @cw.command()
    async def test(self, ctx, a):
        await ctx.send("win")

def setup(bot):
    bot.add_cog(RestartKill(bot))