"""Module that contains functions for waiting for responses."""


import typing as typ
import asyncio
import enum

import nextcord as nx
import nextcord.ext.commands as nx_cmds

import global_vars
import backend.exc_utils.custom_exc as c_e
import backend.exc_utils.send_error as s_e

from . import detection_checks as w_f_ch


TIMEOUT = global_vars.Timeouts.long

TIMEOUT_MESSAGE = "Command timed out. Please use the command again."


async def send_error(ctx, suffix, send_author = False):
    """Sends an error, but with a syntax."""
    await s_e.send_error(ctx, f"{suffix} Try again.", send_author = send_author)


async def wait_for_message(ctx: nx_cmds.Context, timeout = TIMEOUT):
    """Wait for a message then return the response."""
    try:
        response: nx.Message = await global_vars.global_bot.wait_for(
            "message",
            check = w_f_ch.check_message(ctx.author.id, ctx.channel.id),
            timeout = timeout
        )
    except asyncio.TimeoutError as exc:
        await s_e.send_error(ctx, TIMEOUT_MESSAGE)
        raise c_e.ExitFunction() from exc
    return response


class ExampleView(nx.ui.View):
    """An example view."""
    def __init__(self):
        super().__init__()
        self.value = None

    @nx.ui.button(label = "one", style = nx.ButtonStyle.green)
    async def button_one(self, button: nx.ui.Button, interact: nx.Interaction):
        """Button!"""
        self.value = "one"
        self.stop()


async def wait_for_view(ctx: nx_cmds.Context, original_message: nx.Message, view: typ.Type[nx.ui.View] | ExampleView, timeout = TIMEOUT):
    """Waits for an interaction."""
    try:
        await global_vars.global_bot.wait_for("interaction", check = w_f_ch.check_interaction(ctx.author.id, original_message.id), timeout = timeout)
    except asyncio.TimeoutError as exc:
        await s_e.send_error(ctx, TIMEOUT_MESSAGE)
        raise c_e.ExitFunction() from exc
    return view


class DetectionOutputTypes(enum.Enum):
    """A class containing identifiers for outputs of a message or a view."""
    message = "message"
    view = "view"

async def wait_for_message_view(ctx: nx_cmds.Context, original_message: nx.Message, view: typ.Type[nx.ui.View] | ExampleView, timeout = TIMEOUT):
    """Waits for a message then returns (MessageViewCheck.message, message). If instead it was a view interaction, return (MessageViewCheck.view, view) of that interaction."""

    events = [
        global_vars.global_bot.wait_for("message", check = w_f_ch.check_message(ctx.author.id, ctx.channel.id)),
        global_vars.global_bot.wait_for("interaction", check = w_f_ch.check_interaction(ctx.author.id, original_message.id))
    ]

    done, pending = await asyncio.wait(events, timeout = timeout, return_when = asyncio.FIRST_COMPLETED)

    if len(done) == 0:
        await s_e.send_error(ctx, TIMEOUT_MESSAGE)
        raise c_e.ExitFunction()

    result: asyncio.Task = done.pop()
    result = result.result()
    for task in pending:
        task: asyncio.Task = task
        task.cancel()

    if isinstance(result, nx.Message):
        return DetectionOutputTypes.message, result
    if isinstance(result, nx.Interaction):
        return DetectionOutputTypes.view, view

    # REWRITE move this to disc_utils
    raise c_e.InvalidResponse()
