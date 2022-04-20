"""Contains the `CmdInfo` class."""


import typing as typ

import nextcord.ext.commands as nx_cmds

from .. import cmd_params
from . import cmd_perms


class CooldownInfo():
    """Contains info about the cooldown."""
    def __init__(
            self,
            length: int = 0,
            type_: nx_cmds.BucketType = nx_cmds.BucketType.guild
            ):
        self.length = length
        self.type_ = type_


class UsabilityInfo():
    """Contains info about the command's visibility."""
    def __init__(
            self,
            enable: bool = True,
            visible_in_help: bool = True,
            usability_condition: typ.Callable[[nx_cmds.Context], bool] = lambda ctx: True,
            guild_only: bool = True
            ):
        self.enable = enable
        self.visible_in_help = visible_in_help
        self.usability_condition = usability_condition
        self.guild_only = guild_only


class CmdInfo():
    """Contains information about the command."""
    def __init__(
            self,
            description: str | None = None,
            example: list[str] | None = None,
            params: cmd_params.Params | None = None,
            aliases: list[str] | None = None,
            sustained: bool = False,
            cooldown_info: CooldownInfo = CooldownInfo(),
            usability_info: UsabilityInfo = UsabilityInfo(),
            perms: cmd_perms.Permissions = cmd_perms.Permissions(),
            ):
        self.description = description
        self.example = example
        self.params = params
        self.aliases = aliases
        self.sustained = sustained
        self.cooldown_info = cooldown_info
        self.usability_info = usability_info
        self.perms = perms
