"""Contains other important classes."""

# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods


class Match:
    """Structure that contains a dictionary and a value to match it with."""
    def __init__(self, data_dict: dict[object, str], value: object):
        self.data_dict = data_dict
        self.value = value

    def get_name(self):
        """Gets the name of the value."""
        return self.data_dict[self.value]

class Unique():
    """Unique variable!"""
    def __init__(self):
        pass
