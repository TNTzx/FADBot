import discord
import discord.ext.commands as cmds

import main
from Functions import CommandWrappingFunction as cw

class RestartKill(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @cw.command(
        category=cw.Categories.botControl,
        description="Restarts the bot.",
        aliases=["sr"],
        requireGuildAdmin=True
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
        requireGuildAdmin=True
    )
    async def switchkill(self, ctx):
        await ctx.send("Terminated bot.")
        await main.bot.logout()


def setup(bot):
    bot.add_cog(RestartKill(bot))