"""Contains a class for artist structures."""


import backend.utils.new_dataclass as dt


class ArtistStructure(dt.Dataclass):
    """Parent class for artist structures."""
    def get_json_dict(self):
        """Turns the data into a dictionary for sending."""
        data: dict = self.to_dict()
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = str(value)

        return data
