"""Contains a class for artist structures."""


import abc
import requests as req

import backend.utils.new_dataclass as dt


class ArtistStruct(dt.APIDataclass):
    """Parent class for artist structures."""
    # def get_json_dict(self):
    #     """Turns the data into a dictionary for sending."""
    #     data: dict = self.to_one_obj()
    #     for key, value in data.items():
    #         if isinstance(value, dict):
    #             data[key] = str(value)

    #     return data

    @classmethod
    def from_vadb_receive(cls, response: req.models.Response) -> None:
        """Returns an object from this class from VADB's response."""
