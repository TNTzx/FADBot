"""Contains the help command."""


import nextcord.ext.commands as nx_cmds

import backend.discord_utils as disc_utils
import backend.exc_utils as exc_utils

from ... import utils as cog


class CogHelp(cog.RegisteredCog):
    """Contains the help command."""

    @disc_utils.command_wrap(
        category = disc_utils.CategoryBasics,
        cmd_info = disc_utils.CmdInfo(
            description = "WHAT IN THE ACTUAL LIVING ARTIST DID YOU DO",
            params = disc_utils.Params(
                disc_utils.ParamArgument(
                    "[command]",
                    description = "DID YOU SERIOUSLY NEED HELP ON A HELP COMMAND"
                )
            ),
            aliases = ["h"],
            cooldown_info = disc_utils.CooldownInfo(
                length = 1,
                type_ = nx_cmds.BucketType.user
            ),
            usability_info = disc_utils.UsabilityInfo(
                guild_only = False
            )
        )
    )
    async def help(self, ctx: nx_cmds.Context, command_query: str = None):
        """Used to display help on a command."""
        if command_query is None:
            await ctx.send(embed = disc_utils.CmdCategory.generate_embed_all_categories())
            return

        await ctx.send("Getting command help info...")
        try:
            command = disc_utils.DiscordCommand.get_from_name_alias(command_query)
        except ValueError:
            await exc_utils.send_error(ctx, f"The command name / alias `{command_query}` cannot be found! Make sure you typed it correctly!")
            return

        await ctx.send(embed = command.generate_embed())
