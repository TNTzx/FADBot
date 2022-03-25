"""Request exceptions."""


class ChangeReqError(Exception):
    """Base class for change request errors."""



class LogChannelError(ChangeReqError):
    """Base class for all log channel errors."""

class LogChannelsNotFound(LogChannelError):
    """Log channels cannot be found."""

class LogChannelAlreadySet(LogChannelError):
    """The log channel has already been set."""
