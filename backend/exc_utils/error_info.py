"""Contains sending errors."""


import traceback

import nextcord as nx
import nextcord.ext.commands as nx_cmds

import global_vars
import backend.logging as lgr

from . import custom_exc as c_e


ERROR_PREFIX = "**Error!**\n"
FATAL_PREFIX = "**FATAL!!**\n"


async def reset_cooldown(ctx: nx_cmds.Context):
    """Resets the context's command cooldown."""
    ctx.command.reset_cooldown(ctx)


async def send_error_warn(
        messageable: nx.abc.Messageable,
        author: nx.User,
        suffix: str,
        try_again = False
        ):
    """Sends a warning to a channel. Usually used for warning bad user input."""
    try_again_str = "\nTry again." if try_again else ""
    text = f"{ERROR_PREFIX}{author.mention}, {suffix}{try_again_str}"
    await messageable.send(text)


async def send_error_failed_cmd(
        messageable: nx.abc.Messageable,
        author: nx.User,
        suffix: str,
        ):
    """Sends an error for a failed command."""
    text = f"{ERROR_PREFIX}{author.mention}, {suffix}"
    await messageable.send(text)


async def send_error_fatal(
        ctx: nx_cmds.Context,
        exc: Exception | nx_cmds.CommandInvokeError = None
        ):
    """Notifies a fatal error."""
    await reset_cooldown(ctx)


    await global_vars.TNTz.send((
        "Error!\n"
        f"Command used: `{ctx.message.content}`\n"
        f"```{exc}```"
    ))


    if isinstance(exc, nx_cmds.CommandInvokeError):
        error = exc.original
    else:
        error = exc

    formatted_exc = "".join(traceback.format_exception(error))

    print((
        f"A fatal error occurred in command {ctx.command.name}:"
        f"{formatted_exc}"
    ))


    await ctx.send(f"{FATAL_PREFIX}Something bad went wrong. This error has been reported to the owner of the bot.")
    lgr.log_global_exc.error(formatted_exc)


# REFACTOR use channel instead of context
async def send_error(
        channel: nx.TextChannel,
        author: nx.User,
        message: nx.Message,
        suffix: str,
        try_again = False,
        exc: Exception | nx_cmds.CommandInvokeError = None,
        send_owner = False,
        send_console = False,
        cooldown_reset = False
        ):
    """Sends an error to a context."""


    text = f"{ERROR_PREFIX}{author.mention}, {suffix}{try_again_str}"
    tntz: nx.User = global_vars.TNTz

    if send_owner:
        await tntz.send((
            "Error!\n"
            f"Command used: `{message.content}`\n"
            f"```{exc}```"
        ))

    if send_console:
        if hasattr(exc, "original"):
            error = exc.original
        else:
            error = exc

        print(f"Ignoring exception in command {ctx.command}:")
        traceback.print_exception(type(error), error, error.__traceback__)

    if cooldown_reset:
        ctx.command.reset_cooldown(ctx)

    if send_author:
        await ctx.author.send(text)
    else:
        if isinstance(ctx.message.channel, nx.DMChannel):
            channel = ctx.message.channel
            await channel.send(text)
        else:
            await ctx.channel.send(text)
    return


async def error_handle(messageable: nx.abc.Messageable, text: str):
    """Send an error message for a specific error. Exit everything afterwards."""
    await messageable.send(text)
    raise c_e.ExitFunction()


async def cancel_command(ctx: nx_cmds.Context, send_author = False):
    """Cancels the current command."""
    await error_handle("Command cancelled.", ctx, send_author = send_author)

async def timeout_command(ctx: nx_cmds.Context, send_author = False):
    """Command timed out."""
    await error_handle("Command timed out. Please use the command again.", ctx, send_author = send_author)
