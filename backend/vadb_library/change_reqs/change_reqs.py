"""Contains logic for requests."""


from .. import artists as art
from . import req_exts


# TODO alrighty time to go ham, gonna need logs, accepting and denying requests, etc.
# go ham future tent *patpatpat*

class ChangeRequest():
    """Parent class for all requests."""
    def __init__(
                self,
                artist: art.Artist,
            ):
        ...
