"""Contains bot control commands."""


import os
import sys

import nextcord as nx
import nextcord.ext.commands as cmds

from ... import utils as cog

import global_vars.variables as vrs
import backend.logging.loggers as lgr
import backend.command_related.command_wrapper as c_w


class CogBotControl(cog.RegisteredCog):
    """Contains bot control."""

    @c_w.command(
        category = c_w.Categories.bot_control,
        description = "Restarts the bot.",
        aliases = ["sr"],
        guild_only = False,
        req_dev = True,
        show_help = False
    )
    async def switchrestart(self, ctx):
        await ctx.send("Restarting bot...")
        lgr.log_bot_status.info("Restarting bot by cogs...")
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
        lgr.log_bot_status.info("Restarted bot by cogs.")
        print("\n \n Restart break! -------------------------------------- \n \n")


    @c_w.command(
        category = c_w.Categories.bot_control,
        description = "Shuts down the bot.",
        aliases = ["sk"],
        guild_only = False,
        req_dev = True,
    )
    async def switchkill(self, ctx):
        lgr.log_bot_status.info("Closed bot by command.")
        await ctx.send("Terminated bot.")
        await self.bot.close()
        exit()


    @c_w.command(
        category = c_w.Categories.bot_control,
        description = f"Like {vrs.CMD_PREFIX}restart, but hard.",
        aliases = ["srh"],
        guild_only = False,
        req_dev = True,
        show_help = False
    )
    async def switchrestarthard(self, ctx):
        lgr.log_bot_status.info("Initiated hard restart.")
        await ctx.send("Restart initiated!")
        print("\n \n Restart break! Hard! -------------------------------------- \n \n")
        args = ['python'] + [f"\"{sys.argv[0]}\""]
        os.execv(sys.executable, args)
