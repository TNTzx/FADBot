"""Firebase exceptions."""


class FBError(Exception):
    """Base class for all Firebase exceptions."""


class FBNoPath(FBError):
    """No path found in Firebase."""
