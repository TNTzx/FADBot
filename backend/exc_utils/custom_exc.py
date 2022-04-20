"""Custom exceptions!"""


class CustomExc(Exception):
    """Parent class for custom exceptions."""


class ExitFunction(CustomExc):
    """Exited Function."""

class FailedCmd(CustomExc):
    """The command failed."""
