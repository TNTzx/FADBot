"""Contains the custom command class."""


from __future__ import annotations

import typing as typ

import nextcord as nx
import nextcord.ext.commands as nx_cmds

import backend.other as ot
import global_vars

from ....message_utils import embed_utils
from . import cmd_exts


class DiscordCommand():
    """A discord command."""
    all_commands: list[DiscordCommand] = []

    def __init__(
            self,
            command: typ.Callable[[nx_cmds.Context, typ.Any], None],
            info: cmd_exts.CmdInfo = cmd_exts.CmdInfo()
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


    def get_full_name(self):
        """Gets the full name with the command prefix."""
        return f"{global_vars.CMD_PREFIX}{self.name}"


    def get_full_syntax(self):
        """Gets the full syntax of the command."""
        return f"{self.get_full_name()} {self.info.params.get_syntax()}"


    def generate_embed(self):
        """Generates an embed of this command."""

        embed = nx.Embed(
            title = f"Help: {global_vars.CMD_PREFIX}{self.name}",
            color = 0xFFAEAE
        )

        embed.add_field(
            name = "Description",
            value = self.info.description,
            inline = False
        )

        if self.info.aliases is not None:
            aliases = "`, `".join(self.info.aliases)
            embed.add_field(
                name = "Aliases:",
                value = f"`{aliases}`",
                inline = False
            )

        embed_utils.make_horizontal_rule_field(embed)

        if self.info.params is None:
            embed.add_field(
                name = "Syntax:",
                value = f"`{self.get_full_name()}`",
                inline = False
            )
        else:
            emb_syntax_help = self.info.params.get_syntax_help()
            emb_syntax_help = emb_syntax_help.split("\n")
            emb_syntax_help = "\n".join(emb_syntax_help[1:])
            embed.add_field(
                name = "Full Syntax:",
                value = (
                    f"`{self.get_full_syntax()}`\n\n"
                    f"__Parameter descriptions:__\n"
                    f"`{emb_syntax_help}`"
                ),
                inline = False
            )

            if self.info.params.has_splits():
                embed.add_field(
                    name = "All usages:",
                    value = "\n".join(
                        [
                            f"`{self.get_full_name()} {param.get_syntax_arranged()}`"
                            for param in self.info.params.get_all_arrangements()
                        ]
                    ),
                    inline = False
                )

        embed_utils.make_horizontal_rule_field(embed)

        guild_only = "only in servers." if self.info.usability_info.guild_only else "in direct messages and servers."
        embed.add_field(name = f"Can be used {guild_only}", value = "_ _", inline = False)

        if self.info.perms.perms is not None:
            emb_perms = [perm.name.title() for perm in self.info.perms.perms]
            emb_perms = "`, `".join(emb_perms)
            embed.add_field(name = "Only allowed for:", value = f"`{emb_perms}`")

        cooldown = self.info.cooldown_info
        if cooldown.length > 0:
            if cooldown.type_ == nx_cmds.BucketType.guild:
                emb_cl_type = "Entire server"
            elif cooldown.type_ == nx_cmds.BucketType.member:
                emb_cl_type = "Per member"
            elif cooldown.type_ == nx_cmds.BucketType.channel:
                emb_cl_type = "Per channel"
            elif cooldown.type_ == nx_cmds.BucketType.category:
                emb_cl_type = "Per channel category"
            elif cooldown.type_ == nx_cmds.BucketType.role:
                emb_cl_type = "Per role"
            elif cooldown.type_ == nx_cmds.BucketType.user:
                emb_cl_type = "Per user"
            else:
                emb_cl_type = "TNTz messed up, he didn't add another edge case, please ping him"
            cooldown_form = (
                f"Duration: `{ot.format_time(self.info.cooldown_info.length)}`\n"
                f"Applies to: `{emb_cl_type}`"
            )
            embed.add_field(
                name = "Cooldown Info:",
                value = f"{cooldown_form}"
            )

        if self.info.example is not None:
            example_usage_form = "`\n`".join(self.info.example)
            embed.add_field(
                name = "Examples:",
                value = f"`{example_usage_form}`",
                inline = False
            )

        return embed


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
