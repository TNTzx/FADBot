"""Module that contains decorators for choice parameters."""


import nextcord.ext.commands as nx_cmds

import backend.exc_utils as exc_utils


def choice_param(arg, choices: list):
    """A decorator to dictate that there is a choice for a parameter."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if arg not in choices:
                raise TypeError()
            return func(*args, **kwargs)
        return wrapper
    return decorator


def choice_param_cmd(ctx: nx_cmds.Context, arg, choices: list):
    """A decorator to dictate that there is a choice for a parameter. Used for commands. Is a coroutine."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if arg not in choices:
                await exc_utils.SendFailedCmd(
                    error_place = exc_utils.ErrorPlace.from_context(ctx),
                    suffix = (
                        f"Make sure you have the correct parameters! `{arg}` is not a valid parameter.\n"
                        f"The available parameters are `{'`, `'.join(choices)}`."
                    )
                ).send()

            return await func(*args, **kwargs)
        return wrapper
    return decorator
