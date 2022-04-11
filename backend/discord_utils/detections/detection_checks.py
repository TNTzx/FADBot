"""Contains checks for waiting."""


import nextcord as nx


def check_message(author_id: int, text_channel_id: int):
    """Check for messages. Call to get wrapper.
    Returns True if:
    - Author is the same for command initiator and message sender.
    - Channel of message sent is the same as text channel."""

    def wrap(msg: nx.Message):
        return author_id == msg.author.id and msg.channel.id == text_channel_id
    return wrap

def check_interaction(author_id: int, original_message_id: int):
    """Checks for interactions. Call to get wrapper.
    Returns True if:
    - Author is the same for command initiator and interaction sender.
    - Interaction happened on the `original_message`."""

    def wrap(interact: nx.Interaction):
        return author_id == interact.user.id and interact.message.id == original_message_id
    return wrap
