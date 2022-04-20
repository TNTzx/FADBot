"""Usage rights."""


from ... import artist_struct


class UsageRight(artist_struct.ArtistStruct):
    """Defines a usage right."""
    def __init__(
            self,
            description: str | None = None,
            is_verified: bool = True
            ):
        self.description = description
        self.is_verified = is_verified


    def vadb_to_edit_json(self) -> dict | list:
        return {
            "name": self.description,
            "value": self.is_verified
        }


    def firebase_to_json(self):
        return {
            "description": self.description,
            "is_verified": self.is_verified
        }

    @classmethod
    def firebase_from_json(cls, json: dict | list):
        return cls(
            description = json.get("description"),
            is_verified = json.get("is_verified")
        )


class UsageRights(artist_struct.ArtistStruct):
    """Defines a list of usage rights."""
    def __init__(self, usage_rights: list[UsageRight] | None = None):
        self.usage_rights = usage_rights


    def vadb_to_edit_json(self) -> dict | list:
        if self.usage_rights is None:
            return None

        return [usage_right.vadb_to_edit_json() for usage_right in self.usage_rights]


    def firebase_to_json(self):
        if self.usage_rights is None:
            return None

        return [usage_right.firebase_to_json() for usage_right in self.usage_rights]

    @classmethod
    def firebase_from_json(cls, json: dict | list):
        if json is None:
            return cls()

        return cls(
            usage_rights = [
                UsageRight.firebase_from_json(usage_right_json) for usage_right_json in json
            ]
        )
