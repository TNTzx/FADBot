"""Module that contains stuff about files being sent to the VADB API."""


import backend.utils.new_dataclass as dt


class APIFile(dt.APIDataclass):
    """Parent class for files."""


class APIFileKey(dt.APIDataclass):
    """A structure to associate an `APIFile` with a string."""
    def __init__(self, key: str, file: APIFile):
        self.key = key
        self.file = file

    def to_payload(self) -> dict | tuple | list:
        return (self.key, self.file.to_payload())


class APIFileList(dt.APIDataclass):
    """A structure to store `APIFileKey`s."""
    def __init__(self, file_keys: list[APIFileKey]):
        self.file_keys = file_keys

    def __repr__(self) -> str:
        return str(self.to_payload())


    def to_payload(self) -> dict | tuple | list:
        return [file_key.to_payload() for file_key in self.file_keys]
