"""Request exceptions."""


class ChangeReqError(Exception):
    """Base class for change request errors."""


class LogChannelsNotFound(ChangeReqError):
    """Log channels cannot be found."""
