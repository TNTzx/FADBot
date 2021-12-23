"""Module that contains decorators for choice parameters."""

# pylint: disable=line-too-long

import nextcord.ext.commands as cmds

import functions.exceptions.send_error as s_e

def choice_param(arg, choices: list):
    """A decorator to dictate that there is a choice for a parameter."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if arg not in choices:
                raise TypeError
            return func(*args, **kwargs)
        return wrapper
    return decorator

def choice_param_cmd(ctx: cmds.Context, arg, choices: list):
    """A decorator to dictate that there is a choice for a parameter. Used for commands. Is a coroutine."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if arg not in choices:
                await s_e.send_error(ctx, f"Make sure you have the correct parameters! `{arg}` is not a valid parameter.\nThe available parameters are `{'`, `'.join(choices)}`.")
            return func(*args, **kwargs)
        return wrapper
    return decorator
