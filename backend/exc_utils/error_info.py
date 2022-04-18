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


class ErrorSender():
    """Parent class for sending errors to a user."""
    prefix: str = "**Error!**\n"

    def __init__(self, error_send_info: ErrorSendInfo, suffix: str, try_again: bool = False):
        self.error_send_info = error_send_info
        self.suffix = suffix,
        self.try_again = try_again


    def get_text(self):
        """Gets the text."""
        try_again_str = "\nTry again." if self.try_again else ""
        return f"{self.prefix}{self.error_send_info.author.mention}, {self.suffix}{try_again_str}"


    async def send(self):
        """Sends the error."""
        await self.error_send_info.messageable.send(self.get_text())


class SendWarn(ErrorSender):
    """Warnings used for bad user input."""


class SendFailedCmd(ErrorSender):
    """Sends an error for a failed command."""
    async def send(self):
        super().send()
        raise custom_exc.FailedCmd(f"Failed command: {self.suffix}")


class ErrorSenderPredetermined(ErrorSender):
    """An extension of `ErrorInfo` that is predetermined and is common."""
    suffix: str = None
    exit_func: bool = True
    def __init__(self, error_send_info: ErrorSendInfo, try_again: bool = False):
        super().__init__(error_send_info, self.suffix, try_again)


    async def send(self):
        await super().send()
        if self.exit_func:
            raise custom_exc.ExitFunction()


class SendCancel(ErrorSenderPredetermined):
    """Cancels the command."""
    suffix = "Command cancelled."

class SendTimeout(ErrorSenderPredetermined):
    """Sends a timeout."""
    suffix = "Command cancelled."


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
