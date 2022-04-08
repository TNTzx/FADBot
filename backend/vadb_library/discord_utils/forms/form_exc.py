"""Form exceptions."""


class FormException(Exception):
    """Base class for form exceptions."""


class InvalidSectionResponse(FormException):
    """Invalid response for the section."""

class ExitSection(FormException):
    """Section exited."""
