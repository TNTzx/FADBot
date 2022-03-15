"""Usage rights."""


import backend.utils.new_dataclass as dt


class UsageRight(dt.APIDataclass):
    """Defines a usage right."""
    def __init__(
            self,
            description: str | None = None,
            is_verified: bool = True
            ):
        self.description = description
        self.is_verified = is_verified

    # TODO
    @classmethod
    def from_dict_response(cls, response: dict):
        ...


class UsageRights(dt.APIDataclass):
    """Defines a list of usage rights."""
    def __init__(self, usage_rights: list[UsageRight] | None = None):
        self.usage_rights = usage_rights

    def to_one_obj(self) -> list | dict:
        return "\n".join([self.usage_rights.__str__()])
