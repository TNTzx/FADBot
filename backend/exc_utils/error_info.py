"""Contains sending errors."""


import traceback

import nextcord as nx
import nextcord.ext.commands as nx_cmds

import global_vars

from . import custom_exc


class ErrorSendInfo():
    """Contains information on where to send the error and its current information."""
    def __init__(self, messageable: nx.abc.Messageable, author: nx.User):
        self.messageable = messageable
        self.author = author

    @classmethod
    def from_context(cls, ctx: nx_cmds.Context):
        """Constructs an `ErrorSendInfo` with a `Context`."""
        return cls(
            messageable = ctx,
            author = ctx.author
        )


class ErrorInfo():
    """Parent class for sending errors to a user."""
    prefix: str = "**Error!**\n"

    def __init__(self, error_send_info: ErrorSendInfo, suffix: str):
        self.error_send_info = error_send_info
        self.suffix = suffix


    async def send(self, try_again: bool = False):
        """Sends the error."""


class SendWarn(ErrorInfo):
    """Warnings used for bad user input."""
    async def send(self, try_again: bool = False):
        try_again_str = "\nTry again." if try_again else ""
        text = f"{self.prefix}{self.error_send_info.author.mention}, {self.suffix}{try_again_str}"
        await self.error_send_info.messageable.send(text)


class SendFailedCmd(ErrorInfo):
    """Sends an error for a failed command."""
    async def send(self, try_again: bool = False):
        text = f"{self.prefix}{self.error_send_info.author.mention}, {self.suffix}"
        await self.error_send_info.messageable.send(text)
        raise custom_exc.FailedCmd(f"Failed command: {self.suffix}")


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
    raise custom_exc.ExitFunction()


async def cancel_command(ctx: nx_cmds.Context, send_author = False):
    """Cancels the current command."""
    await error_handle("Command cancelled.", ctx, send_author = send_author)

async def timeout_command(ctx: nx_cmds.Context, send_author = False):
    """Command timed out."""
    await error_handle("Command timed out. Please use the command again.", ctx, send_author = send_author)
