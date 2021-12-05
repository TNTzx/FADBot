# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=no-self-use
# pylint: disable=too-many-branches

import os
import sys

import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import functions.command_related.command_wrapper as c_w


class RestartKill(cmds.Cog):
    def __init__(self, bot: nx.Client):
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
        for file in os.listdir(os.path.dirname(__file__)):
            if file.endswith(".py"):
                if file == "__init__.py":
                    continue
                new_file = f"{file[:-3]}"

                try:
                    self.bot.unload_extension(new_file)
                except cmds.errors.ExtensionNotLoaded:
                    continue
                self.bot.load_extension(new_file)
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
        await self.bot.close()
        exit()


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

def setup(bot):
    """Sets the bot up."""
    bot.add_cog(RestartKill(bot))
