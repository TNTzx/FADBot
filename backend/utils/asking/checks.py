"""Contains checks for waiting."""


import nextcord as nx
import nextcord.ext.commands as cmds


def check_message_dm(ctx: cmds.Context):
    """Check for messages. Call to get wrapper.
    Returns True if:
    - Author is the same for command initiator and message sender.
    - Channel sent is a DMChannel."""

    def wrap(msg: nx.Message):
        return ctx.author.id == msg.author.id and isinstance(msg.channel, nx.channel.DMChannel)
    return wrap

def check_interaction(ctx: cmds.Context, original_message: nx.Message):
    """Checks for interactions. Call to get wrapper.
    Returns True if:
    - Author is the same for command initiator and interaction sender.
    - Interaction happened on the original_message."""

    def wrap(interact: nx.Interaction):
        return ctx.author.id == interact.user.id and interact.message.id == original_message.id
    return wrap
