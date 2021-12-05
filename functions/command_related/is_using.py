"""Module that contains functions to check, add, and delete users using a command."""

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=too-many-statements
# pylint: disable=line-too-long
# pylint: disable=unused-argument


import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import functions.databases.firebase.firebase_interaction as f_i
import functions.exceptions.custom_exc as c_e
import functions.exceptions.send_error as s_e


def check_if_using_command(path: list[str], author_id: int):
    """Returns true if the user is using the command."""
    users_using = f_i.get_data(path)
    return str(author_id) in list(users_using)

def add_is_using_command(path: list[str], author_id: int):
    """Adds the user as one that is using the command."""
    f_i.append_data(path, [str(author_id)])

def delete_is_using_command(path: list[str], author_id: int):
    """Deletes the user as one that is using the command."""
    f_i.deduct_data(path, [str(author_id)])

def delete_all_is_using():
    """Deletes all entries on paths in sustained commands."""
    for sustained_cmd in LIST_OF_SUSTAINED_CMDS:
        f_i.override_data(sustained_cmd.path, vrs.PLACEHOLDER_DATA)


class SustainedCommand:
    """A class that stores info about a command that requires tracking of who's using it."""
    def __init__(self, cmd_name: str, path: list[str]):
        self.cmd_name = cmd_name
        self.path = path

LIST_OF_SUSTAINED_CMDS: list[SustainedCommand] = []


def sustained_command():
    """A decorator factory for sustained commands."""
    def decorator(func):
        path = ["commandData", "isUsingCommand", str(func.__name__)]

        if not f_i.is_data_exists(path):
            f_i.override_data(path, vrs.PLACEHOLDER_DATA)

        async def wrapper(*args, **kwargs):
            ctx: cmds.Context = args[1]

            if check_if_using_command(path, ctx.author.id):
                await s_e.send_error(ctx, f"You're already using this command! Use {vrs.CMD_PREFIX}cancelall on your DMs with me to cancel the command.")
                return

            add_is_using_command(path, ctx.author.id)

            try:
                await func(*args, **kwargs)
            except Exception as exc:
                delete_is_using_command(path, ctx.author.id)
                if isinstance(exc, c_e.ExitFunction):
                    pass
                raise exc

            delete_is_using_command(path, ctx.author.id)

        LIST_OF_SUSTAINED_CMDS.append(SustainedCommand(func.__name__, path))

        return wrapper

    return decorator
