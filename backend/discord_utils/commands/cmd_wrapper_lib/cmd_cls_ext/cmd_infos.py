"""Contains the `CmdInfo` class."""


import nextcord.ext.commands as nx_cmds

from . import privilege_reqs


class CooldownInfo():
    """Contains info about the cooldown."""
    def __init__(
            self,
            length: int = 0,
            type_: nx_cmds.BucketType = nx_cmds.BucketType.guild
            ):
        self.length = length
        self.type_ = type_


class CmdInfo():
    """Contains information about the command."""
    def __init__(
            self,
            description: str | None = None,
            parameters: dict[str, str] | None = None,
            aliases: list[str] | None = None,
            cooldown: CooldownInfo = CooldownInfo(),
            priv_req_list: 
            ):
        pass

