"""Contains sending errors."""


import nextcord as nx
import nextcord.ext.commands as nx_cmds

from . import custom_exc


class ErrorPlace():
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

    def __init__(self, error_place: ErrorPlace, suffix: str, try_again: bool = False):
        self.error_place = error_place
        self.suffix = suffix
        self.try_again = try_again


    def get_text(self):
        """Gets the text."""
        try_again_str = "\nTry again." if self.try_again else ""
        return f"{self.prefix}{self.error_place.author.mention}, {self.suffix}{try_again_str}"


    async def send(self):
        """Sends the error."""
        await self.error_place.messageable.send(self.get_text())


class SendWarn(ErrorSender):
    """Warnings used for bad user input."""


class SendFailed(ErrorSender):
    """Sends an error for fails, exiting the function with `ExitFunction`."""
    async def send(self):
        await super().send()
        raise custom_exc.ExitFunction()


class SendFailedCmd(ErrorSender):
    """Sends an error for a failed command."""
    async def send(self):
        await super().send()
        raise custom_exc.FailedCmd(f"Failed command: {self.suffix}")


class ErrorSenderPredetermined(ErrorSender):
    """An extension of `ErrorInfo` that is predetermined and is common."""
    suffix: str = None
    exit_func: bool = True
    def __init__(self, error_place: ErrorPlace, try_again: bool = False):
        super().__init__(error_place, self.suffix, try_again)


    async def send(self):
        await super().send()
        if self.exit_func:
            raise custom_exc.ExitFunction()


class SendCancel(ErrorSenderPredetermined):
    """Cancels the command."""
    suffix = "Command cancelled."

class SendTimeout(ErrorSenderPredetermined):
    """Sends a timeout."""
    suffix = "Command timed out."
