"""Contains sending errors."""


import traceback

import nextcord as nx
import nextcord.ext.commands as nx_cmds

import global_vars

from . import custom_exc as c_e


ERROR_PREFIX = "**Error!**\n"

async def send_error(ctx: nx_cmds.Context, suffix, exc = "", other_data: nx.Message = None,
        send_author = False, send_owner = False, send_console = False, cooldown_reset = False):
    """Sends an error to a context."""

    text = f"{ERROR_PREFIX}{ctx.author.mention}, {suffix}"
    tntz: nx.User = global_vars.TNTz

    if send_owner:
        extra = ""
        if not other_data is None:
            extra = f"\nOther Data: `{vars(other_data)}"

        await tntz.send((
            "Error!\n"
            f"Command used: `{ctx.message.content}`{extra}\n"
            f"```{exc}```"
        ))

    if send_console:
        error = getattr(exc, 'original', exc)
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


async def error_handle(message: str, ctx: nx_cmds.Context, send_author = False):
    """Send an error message for a specific error. Exit everything afterwards."""
    if send_author:
        await ctx.author.send(message)
    else:
        await ctx.send(message)

    raise c_e.ExitFunction()



async def cancel_command(ctx: nx_cmds.Context, send_author = False):
    """Cancels the current command."""
    await error_handle("Command cancelled.", ctx, send_author = send_author)

async def timeout_command(ctx: nx_cmds.Context, send_author = False):
    """Command timed out."""
    await error_handle("Command timed out. Please use the command again.", ctx, send_author = send_author)
