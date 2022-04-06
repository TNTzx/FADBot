"""Contains checks for certain cases then sends an error if cases are not met.
If conditions are met, the object being checked will be returned."""


import nextcord as nx
import nextcord.ext.commands as nx_cmds

import global_vars.variables as vrs
import backend.exc_utils.custom_exc as c_e
import backend.exc_utils.send_error as s_e
import backend.other_functions as o_f


async def channel_from_mention(ctx: nx_cmds.Context, channel_mention: str):
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

async def get_user_from_id(ctx: nx_cmds.Context, user_id: int):
    """Takes in a user ID and returns the user. Sends an error if failed."""

    user = vrs.global_bot.get_user(user_id)
    if user is None:
        await s_e.send_error(ctx, "The user does not exist.")
        raise c_e.ExitFunction()

    return user
