"""Contains the request structure."""


import backend.utils.new_dataclass as dt


class RequestStruct(dt.Dataclass):
    """A request structure."""

    def to_json_firebase(self):
        """Turns this `RequestStruct` to a JSON for firebase."""

    @classmethod
    def from_json_firebase(cls, json: dict | list):
        """Returns the `RequestStruct` equivalent of this JSON from firebase."""
