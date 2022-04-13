"""Contains a class for prefix manipulation."""


from __future__ import annotations


class Indent():
    """A class for logic on prefixes."""
    def __init__(self, indent_char = "--  ", indent_level = 0):
        self.char = indent_char
        self.level = indent_level

    def __str__(self):
        return self.get_str()


    def get_str(self):
        """Gets the string representation of this `PrefixStr`."""
        return self.char * self.level
