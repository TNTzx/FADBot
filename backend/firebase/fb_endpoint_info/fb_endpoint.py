"""Contains a class for a firebase endpoint."""


from __future__ import annotations


class FBEndpoint():
    """A Firebase endpoint."""
    def __init__(self, name: str = None, parent: FBEndpoint = None):
        self.name = name
        self.parent = parent


    def get_path(self):
        """Gets the path to this endpoint."""
        path = [self.name]
        current_parent = self.parent

        while True:
            path.append(current_parent.name)
            current_parent = current_parent.parent

            if current_parent is None:
                return list(reversed(path))
