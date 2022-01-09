"""Contains checks for certain cases then sends an error if cases are not met.
If conditions are met, the object being checked will be returned."""


# pylint: disable=line-too-long


import nextcord as nx
import nextcord.ext.commands as cmds

import backend.exceptions.custom_exc as c_e
import backend.exceptions.send_error as s_e
import backend.other_functions as o_f


async def channel_from_mention(ctx: cmds.Context, channel_mention: str):
    """Takes in a channel mention then returns the channel. Sends an error if failed."""
    async def send_not_found():
        await s_e.send_error(ctx, "You didn't send a valid channel mention! Make sure that the channel is highlighted blue for the command to work!")
        raise c_e.ExitFunction()

    channel = await o_f.get_channel_from_mention(channel_mention)

    if channel is None or \
            not isinstance(channel, nx.TextChannel) or \
            channel not in ctx.guild.text_channels:
        await send_not_found()

    return channel
