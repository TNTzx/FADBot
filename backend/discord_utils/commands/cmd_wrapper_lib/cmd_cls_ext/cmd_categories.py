"""Contains logic for command categories."""


from . import cmd_cls


class CmdCategory():
    """Parent class for command categories."""
    commands: list[cmd_cls.DiscordCommand] = []


    @classmethod
    def get_all_categories(cls):
        """Gets all command categories."""
        return cls.__subclasses__()


    @classmethod
    def register_command(cls, cmd: cmd_cls.DiscordCommand):
        """Registers a command under this category."""
        cls.commands.append(cmd)


# TODO do all command categories
