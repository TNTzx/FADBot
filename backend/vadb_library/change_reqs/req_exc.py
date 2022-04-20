"""Request exceptions."""


class ChangeReqError(Exception):
    """Base class for change request errors."""



class LogChannelError(ChangeReqError):
    """Base class for all log channel errors."""

class LogChannelsNotFound(LogChannelError):
    """Log channels cannot be found."""

class LogChannelAlreadySet(LogChannelError):
    """The log channel has already been set."""


class ChangeReqNotFound(ChangeReqError):
    """The change request cannot be found."""


class ChangeReqNotSubmitted(ChangeReqError):
    """The change request hasn't been submitted to Firebase yet."""
    def __init__(self) -> None:
        super().__init__("Artist not submitted in Firebase yet.")


class SetApprovalCancelled(ChangeReqError):
    """Setting an approval has been cancelled."""
    def __init__(self) -> None:
        super().__init__(self.__class__.__doc__)
