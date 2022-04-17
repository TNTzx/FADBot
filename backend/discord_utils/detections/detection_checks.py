"""Contains checks for waiting."""


import nextcord as nx


def check_message(author: nx.User, text_channel: nx.TextChannel):
    """Check for messages. Call to get wrapper.
    Returns True if:
    - Author is the same for command initiator and message sender.
    - Channel of message sent is the same as text channel."""

    def wrap(msg: nx.Message):
        return author.id == msg.author.id and text_channel.id == msg.channel.id
    return wrap

# REWRITE change to only use an author and message
def check_interaction(author_id: int, original_message_id: int):
    """Checks for interactions. Call to get wrapper.
    Returns True if:
    - Author is the same for command initiator and interaction sender.
    - Interaction happened on the `original_message`."""

    def wrap(interact: nx.Interaction):
        return author_id == interact.user.id and interact.message.id == original_message_id
    return wrap
