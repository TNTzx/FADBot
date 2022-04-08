"""Contains bot control commands."""


import os
import sys

import nextcord.ext.commands as nx_cmds

import global_vars
import backend.logging.loggers as lgr
import backend.discord_utils as disc_utils

from ... import utils as cog


class CogBotControl(cog.RegisteredCog):
    """Contains bot control."""

    @disc_utils.command(
        category = disc_utils.CmdCategories.bot_control,
        description = "Restarts the bot.",
        aliases = ["sr"],
        guild_only = False,
        req_dev = True,
        show_help = False
    )
    async def switchrestart(self, ctx: nx_cmds.Context):
        """Restarts the bot."""
        await ctx.send("Restarting bot...")
        lgr.log_bot_status.info("Restarting bot by cogs...")
        for file in os.listdir(os.path.dirname(__file__)):
            if file.endswith(".py"):
                if file == "__init__.py":
                    continue
                new_file = f"{file[:-3]}"

                try:
                    self.bot.unload_extension(new_file)
                except nx_cmds.errors.ExtensionNotLoaded:
                    continue
                self.bot.load_extension(new_file)
        await ctx.send("Restarted!")
        lgr.log_bot_status.info("Restarted bot by cogs.")
        print("\n \n Restart break! -------------------------------------- \n \n")


    @disc_utils.command(
        category = disc_utils.CmdCategories.bot_control,
        description = "Shuts down the bot.",
        aliases = ["sk"],
        guild_only = False,
        req_dev = True,
    )
    async def switchkill(self, ctx: nx_cmds.Context):
        """Kills the bot."""
        lgr.log_bot_status.info("Closed bot by command.")
        await ctx.send("Terminated bot.")
        await self.bot.close()
        sys.exit()


    @disc_utils.command(
        category = disc_utils.CmdCategories.bot_control,
        description = f"Like {global_vars.CMD_PREFIX}restart, but hard.",
        aliases = ["srh"],
        guild_only = False,
        req_dev = True,
        show_help = False
    )
    async def switchrestarthard(self, ctx: nx_cmds.Context):
        """Restarts the bot hard."""
        lgr.log_bot_status.info("Initiated hard restart.")
        await ctx.send("Restart initiated!")
        print("\n \n Restart break! Hard! -------------------------------------- \n \n")
        args = ['python'] + [f"\"{sys.argv[0]}\""]
        os.execv(sys.executable, args)
