"""Module that contains functions for waiting for responses."""


import typing as typ
import asyncio
import enum

import nextcord as nx

import global_vars
import backend.exc_utils as exc_utils

from .. import disc_exc
from . import detection_checks as w_f_ch


TIMEOUT = global_vars.Timeouts.long

TIMEOUT_MESSAGE = "Command timed out. Please use the command again."


async def wait_for_message(
        channel: nx.TextChannel,
        author: nx.User,
        timeout = TIMEOUT
        ):
    """Wait for a message then return the response."""
    try:
        response: nx.Message = await global_vars.bot.wait_for(
            "message",
            check = w_f_ch.check_message(author, channel),
            timeout = timeout
        )
    except asyncio.TimeoutError:
        await exc_utils.SendTimeout(
            error_place = exc_utils.ErrorPlace(channel, author)
        ).send()

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


async def wait_for_view(
        channel: nx.TextChannel,
        author: nx.User,
        original_message: nx.Message,
        view: typ.Type[nx.ui.View] | ExampleView,
        timeout = TIMEOUT
        ):
    """Waits for an interaction."""
    try:
        await global_vars.bot.wait_for(
            "interaction",
            check = w_f_ch.check_interaction(author, original_message),
            timeout = timeout
        )
    except asyncio.TimeoutError:
        await exc_utils.SendTimeout(
            error_place = exc_utils.ErrorPlace(channel, author)
        ).send()
    return view


class DetectionOutputTypes(enum.Enum):
    """A class containing identifiers for outputs of a message or a view."""
    MESSAGE = "message"
    VIEW = "view"


async def wait_for_message_view(
        channel: nx.TextChannel,
        author: nx.User,
        original_message: nx.Message,
        view: typ.Type[nx.ui.View] | ExampleView,
        timeout = TIMEOUT
        ):
    """Waits for a message then returns (MessageViewCheck.message, message). If instead it was a view interaction, return (MessageViewCheck.view, view) of that interaction."""

    events = [
        global_vars.bot.wait_for(
            "message",
            check = w_f_ch.check_message(author, channel)
        ),
        global_vars.bot.wait_for(
            "interaction",
            check = w_f_ch.check_interaction(author, original_message)
        )
    ]

    done, pending = await asyncio.wait(events, timeout = timeout, return_when = asyncio.FIRST_COMPLETED)

    if len(done) == 0:
        await exc_utils.SendTimeout(
            error_place = exc_utils.ErrorPlace(channel, author)
        ).send()

    result: asyncio.Task = done.pop()
    result = result.result()
    for task in pending:
        task: asyncio.Task = task
        task.cancel()

    if isinstance(result, nx.Message):
        return DetectionOutputTypes.MESSAGE, result
    if isinstance(result, nx.Interaction):
        return DetectionOutputTypes.VIEW, view

    raise disc_exc.InvalidResponse("Invalid response.")
