"""Module that contains functions to check, add, and delete users using a command."""


import functools as fc
import nextcord.ext.commands as nx_cmds

import global_vars.variables as vrs
import backend.firebase as firebase
import backend.exceptions.custom_exc as c_e
import backend.exceptions.send_error as s_e


def check_if_using_command(path: list[str], author_id: int):
    """Returns true if the user is using the command."""
    users_using = firebase.get_data(path, default = [])
    return str(author_id) in list(users_using)

def add_is_using_command(path: list[str], author_id: int):
    """Adds the user as one that is using the command."""
    firebase.append_data(path, [str(author_id)])

def delete_is_using_command(path: list[str], author_id: int):
    """Deletes the user as one that is using the command."""
    try:
        firebase.deduct_data(path, [str(author_id)])
    except c_e.FirebaseNoEntry:
        return

def delete_all_is_using():
    """Deletes all entries on paths in sustained commands."""
    for sustained_cmd in LIST_OF_SUSTAINED_CMDS:
        firebase.override_data(sustained_cmd.path, firebase.PLACEHOLDER_DATA)


class SustainedCommand:
    """A class that stores info about a command that requires tracking of who's using it."""
    def __init__(self, cmd_name: str, path: list[str]):
        self.cmd_name = cmd_name
        self.path = path

LIST_OF_SUSTAINED_CMDS: list[SustainedCommand] = []


def sustained_command():
    """A decorator factory for sustained commands."""
    def decorator(func):
        path = firebase.ENDPOINTS.e_discord.e_commands.e_is_using.get_path() + [str(func.__name__)]

        if not firebase.is_data_exists(path):
            firebase.override_data(path, [firebase.PLACEHOLDER_DATA])

        @fc.wraps(func)
        async def wrapper(*args, **kwargs):
            ctx: nx_cmds.Context = args[1]

            if check_if_using_command(path, ctx.author.id):
                await s_e.send_error(ctx, "You're already using this command! Please cancel the command you're currently using, or wait until it times out!")
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
