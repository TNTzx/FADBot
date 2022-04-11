"""Contains the custom command class."""


from __future__ import annotations

import typing as typ

import nextcord.ext.commands as nx_cmds

from . import cmd_infos


class DiscordCommand():
    """A discord command."""
    all_commands: list[DiscordCommand] = []

    def __init__(
            self,
            command: typ.Callable[[nx_cmds.Context, typ.Any], None],
            info: cmd_infos.CmdInfo = cmd_infos.CmdInfo()
            ):
        self.command = command
        self.name = command.__name__
        self.info = info

        self.__class__.all_commands.append(self)


    def get_shorthand(self):
        """
        Gets the shorthand name of this command.
        `<name> (<alias, if any>)
        """
        if self.info.aliases is None:
            return self.name

        return f"{self.name} ({', '.join(self.info.aliases)})"


    # TODO generate an embed of a discord command
    def generate_embed(self):
        """Generates an embed."""


    @classmethod
    def get_all_commands(cls):
        """Gets all commands."""
        return cls.all_commands

    @classmethod
    def get_from_name_alias(cls, name_alias: str):
        """Returns a command based on its name or alias."""
        for command in cls.get_all_commands():
            if name_alias in \
                    [command.name] + (
                        command.info.aliases
                        if command.info.aliases is not None
                        else []
                    ):
                return command

        raise ValueError(f"Name / alias {name_alias} not found.")
