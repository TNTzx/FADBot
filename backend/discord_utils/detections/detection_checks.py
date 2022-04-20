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


def check_interaction(author: nx.User, original_message: nx.Message):
    """Checks for interactions. Call to get wrapper.
    Returns True if:
    - Author is the same for command initiator and interaction sender.
    - Interaction happened on the `original_message`."""

    def wrap(interact: nx.Interaction):
        return author.id == interact.user.id and original_message.id == interact.message.id
    return wrap
