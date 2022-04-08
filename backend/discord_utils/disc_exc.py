"""Contains custom Discord exceptions."""


import nextcord as nx


class CustomDiscordException(nx.errors.DiscordException):
    """A custom Discord exception."""


class GetError(CustomDiscordException):
    """Getting a channel or user from ID didn't go well."""

class GetNotFound(GetError):
    """Getting something wasn't found. Usually is raised when the request returns None."""

class ChannelNotFound(GetNotFound):
    """Channel not found."""
    def __init__(self, channel_id: int):
        super().__init__(f"Channel ID \"{channel_id}\" not found.")

class UserNotFound(GetNotFound):
    """User not found."""
    def __init__(self, user_id: int):
        super().__init__(f"User ID \"{user_id}\" not found.")


class NotMention(CustomDiscordException):
    """Not a mention string."""
    def __init__(self, not_mention_str: str):
        super().__init__(f"\"{not_mention_str}\" is not a mention string.")


class InvalidResponse(CustomDiscordException):
    """Invalid response to a prompt."""
