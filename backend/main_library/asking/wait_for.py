"""Module that contains functions for waiting for responses."""

# pylint: disable=line-too-long
# pylint: disable=no-else-raise
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements

import typing as typ
import asyncio
import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import backend.exceptions.custom_exc as c_e
import backend.exceptions.send_error as s_e


TIMEOUT = 60 * 10


async def send_error(ctx, suffix):
    """Sends an error, but with a syntax."""
    await s_e.send_error(ctx, f"{suffix} Try again.", send_author=True)

async def wait_for_response(ctx: cmds.Context, timeout=TIMEOUT):
    """Wait for a message then return the response."""
    try:
        check = lambda msg: ctx.author.id == msg.author.id and isinstance(msg.channel, nx.channel.DMChannel)
        response: nx.Message = await vrs.global_bot.wait_for("message", check=check, timeout=timeout)

    except asyncio.TimeoutError as exc:
        await s_e.send_error(ctx, "Command timed out. Please use the command again.")
        raise c_e.ExitFunction("Exited Function.") from exc
    return response

async def wait_for_response_view(ctx: cmds.Context, view: typ.Type[nx.ui.View], timeout=TIMEOUT):
    """Waits for a message then returns that message. If instead it was a view interaction, return the value of that interaction."""
    
