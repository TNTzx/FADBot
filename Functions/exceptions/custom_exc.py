"""Custom exceptions!"""

class ExitFunction(Exception):
    """Exited Function."""

class FirebaseNoEntry(Exception):
    """There's no entry in the Firebase Database."""

class DictOverrideError(Exception):
    """Override doesn't have an entry in default."""
