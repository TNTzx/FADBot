"""The main structures."""


import backend.utils.new_dataclass as dt


class FBStruct(dt.Dataclass):
    """Structure for Firebase-related operations."""
    def firebase_to_json(self):
        """Returns the JSON of this `FBStruct`."""
        raise ValueError("\"firebase_to_json\" not supported for this FBStruct.")

    @classmethod
    def firebase_from_json(cls):
        """Returns the `FBStruct` of this JSON."""
        raise ValueError("\"firebase_from_json\" not supported for this FBStruct.")
