"""Usage rights."""


import backend.utils.new_dataclass as dt

from ... import artist_struct as a_s


class UsageRight(dt.Dataclass):
    """Defines a usage right."""
    def __init__(
            self,
            description: str | None = None,
            is_verified: bool = True
            ):
        self.description = description
        self.is_verified = is_verified


class UsageRights(dt.Dataclass):
    """Defines a list of usage rights."""
    def __init__(self, usage_rights: list[UsageRight] | None = None):
        self.usage_rights = usage_rights
