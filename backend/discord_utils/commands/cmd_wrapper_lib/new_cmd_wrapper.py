"""Contains the command wrapper."""


import typing as typ

from . import cmd_cls_lib as cmd_ext


def command_wrap(
        category: typ.Type[cmd_ext.CmdUsageRequ],
        cmd_info: cmd_ext.CmdInfo = cmd_ext.CmdInfo()
        ):
    """Registers this function as a command."""
