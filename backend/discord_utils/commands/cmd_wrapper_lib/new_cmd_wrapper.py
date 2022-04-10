"""Contains the command wrapper."""


import typing as typ
import functools

import nextcord.ext.commands as nx_cmds

import backend.exc_utils as exc_utils

from . import cmd_cls_lib as cmd_ext
from . import cmd_wrap_excs


def command_wrap(
        category: typ.Type[cmd_ext.CmdCategory],
        cmd_info: cmd_ext.CmdInfo = cmd_ext.CmdInfo()
        ):
    """A decorator factory that registers this function as a command to a category with its relevant info."""
    def decorator(cmd_func):
        @functools.wraps()
        async def wrapper(cog, ctx: nx_cmds.Context, *args, **kwargs):
            requ_check = cmd_info.usage_requs.has_met_all_requs(ctx)
            if not requ_check[0]:
                failed_requ_check = requ_check[1]
                await exc_utils.send_error(ctx, failed_requ_check.get_full_fail_message(), cooldown_reset = True)
                raise cmd_wrap_excs.PrivilegeReqNotMet(failed_requ_check.__class__.__name__)

            if not cmd_info.usability_info.usability_condition(ctx):
                ctx.command.reset_cooldown(ctx)
                return

            return await cmd_func(*args, **kwargs)

        cmd_aliases = cmd_info.aliases
        if cmd_aliases is None:
            wrapper = nx_cmds.command(name = cmd_func.__name__)(wrapper)
        else:
            wrapper = nx_cmds.command(name = cmd_func.__name__, aliases = cmd_aliases)(wrapper)

        if cmd_info.usability_info.guild_only:
            wrapper = nx_cmds.guild_only()(wrapper)

        if cmd_info.cooldown_info.length > 0:
            wrapper = nx_cmds.cooldown(
                1,
                cmd_info.cooldown_info.length,
                cmd_info.cooldown_info.type_
            )(wrapper)


        cmd = cmd_ext.DiscordCommand(
            command = wrapper,
            info = cmd_info
        )
        category.register_command(cmd)

        return wrapper

    return decorator
