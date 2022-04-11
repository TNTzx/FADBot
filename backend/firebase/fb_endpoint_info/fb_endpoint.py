"""Contains a class for a firebase endpoint."""


from __future__ import annotations


class FBEndpoint():
    """The base class of all Firebase endpoints."""
    def __init__(self, name: str, parent: FBEndpoint = None):
        self.name = name
        self.parent = parent

    def __repr__(self):
        return f"FBEndpoint({self.name})"


    def get_path(self):
        """Gets the path to this endpoint."""
        path = [self.name]
        current_parent = self.parent

        while True:
            if current_parent.parent is None:
                break

            path.append(current_parent.name)
            current_parent = current_parent.parent

        return list(reversed(path))


class FBEndpointRoot(FBEndpoint):
    """A root Firebase endpoint."""
    def __init__(self):
        super().__init__(name = None, parent = None)


class FBEndpointParent(FBEndpoint):
    """A parent Firebase endpoint."""
    def __init__(self, name: str, parent: FBEndpoint):
        super().__init__(name, parent)


class FBEndpointEnd(FBEndpointParent):
    """An ending Firebase endpoint."""
    def get_default_data(self):
        """Gets the default data for this `FBEndpointEnd`. Used to create stuff."""
        raise ValueError("get_default_data not implemented.")
