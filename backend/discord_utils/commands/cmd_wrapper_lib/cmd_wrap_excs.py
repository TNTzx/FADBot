"""Contains errors for command wrapping exceptions."""


from ... import disc_exc


class CmdWrapError(disc_exc.CustomDiscordException):
    """An error relating to command wrapping has occured."""


class UsageReqNotMet(CmdWrapError):
    """The privilege hasn't been met."""
    def __init__(self, cls_name: str):
        super().__init__(f"Privilege requirement {cls_name} not met for current context.")
