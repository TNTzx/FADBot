# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=no-self-use

import os
import sys

# import discord
import discord.ext.commands as cmds

import main
from global_vars import variables as vrs
from functions import command_wrapper as c_w


class RestartKill(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c_w.command(
        category=c_w.Categories.bot_control,
        description="Restarts the bot.",
        aliases=["sr"],
        guild_only=False,
        req_dev=True,
    )
    async def switchrestart(self, ctx):
        await ctx.send("Restarting bot...")
        main.restart_bot()
        await ctx.send("Restarted!")
        print("\n \n Restart break! -------------------------------------- \n \n")


    @c_w.command(
        category=c_w.Categories.bot_control,
        description="Shuts down the bot.",
        aliases=["sk"],
        guild_only=False,
        req_dev=True
    )
    async def switchkill(self, ctx):
        await ctx.send("Terminated bot.")
        await main.bot.logout()


    @c_w.command(
        category=c_w.Categories.bot_control,
        description=f"Like {vrs.CMD_PREFIX}restart, but hard.",
        aliases=["srh"],
        guild_only=False,
        req_dev=True
    )
    async def switchrestarthard(self, ctx):
        await ctx.send("Restart initiated!")
        print("\n \n Restart break! Hard! -------------------------------------- \n \n")
        args = ['python'] + [f"\"{sys.argv[0]}\""]
        os.execv(sys.executable, args)


    @c_w.command(
        req_pa_mod=True
    )
    async def test(self, ctx):
        # ...hey, uhm, man, you doing alright? Make sure to take some breaks okay? You need it! - past you
        await ctx.send("win")

def setup(bot):
    """Sets the bot up."""
    bot.add_cog(RestartKill(bot))
