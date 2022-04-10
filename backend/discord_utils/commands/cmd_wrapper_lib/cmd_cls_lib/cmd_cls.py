"""Contains the custom command class."""


import nextcord.ext.commands as nx_cmds

import typing as typ

from . import cmd_infos


class DiscordCommand():
    """A discord command."""
    def __init__(
            self,
            command: typ.Callable[[nx_cmds.Context, typ.Any], None],
            info: cmd_infos.CmdInfo = cmd_infos.CmdInfo()
            ):
        self.command = command
        self.info = info