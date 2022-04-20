"""Contains bot control commands."""


import os
import sys

import nextcord.ext.commands as nx_cmds

import backend.logging as lgr
import backend.discord_utils as disc_utils

from ... import utils as cog


class CogBotControl(cog.RegisteredCog):
    """Contains bot control."""

    @disc_utils.command_wrap(
        category = disc_utils.CategoryBotControl,
        cmd_info = disc_utils.CmdInfo(
            description = "Restarts the bot.",
            aliases = ["sr"],
            usability_info = disc_utils.UsabilityInfo(
                visible_in_help = False,
                guild_only = False
            ),
            perms = disc_utils.Permissions(
                [disc_utils.PermDev]
            )
        )
    )
    async def switchrestart(self, ctx: nx_cmds.Context):
        """Restarts the bot."""
        lgr.log_bot_status.info("Initiated hard restart.")
        await ctx.send("Restart initiated!")
        print("\n \n Restart break! Hard! -------------------------------------- \n \n")
        args = ['python'] + [f"\"{sys.argv[0]}\""]
        os.execv(sys.executable, args)


    @disc_utils.command_wrap(
        category = disc_utils.CategoryBotControl,
        cmd_info = disc_utils.CmdInfo(
            description = "Shuts down the bot.",
            aliases = ["sk"],
            usability_info = disc_utils.UsabilityInfo(
                visible_in_help = False,
                guild_only = False
            ),
            perms = disc_utils.Permissions(
                [disc_utils.PermDev]
            )
        )
    )
    async def switchkill(self, ctx: nx_cmds.Context):
        """Kills the bot."""
        lgr.log_bot_status.info("Closed bot by command.")
        await ctx.send("Terminated bot.")
        await self.bot.close()
        sys.exit()
