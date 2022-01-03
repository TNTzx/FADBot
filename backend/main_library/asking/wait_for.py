"""Module that contains functions for waiting for responses."""

# pylint: disable=line-too-long
# pylint: disable=no-else-raise
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=unused-argument


import typing as typ
import asyncio
import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import backend.main_library.asking.checks as w_f_ch
import backend.exceptions.custom_exc as c_e
import backend.exceptions.send_error as s_e
import backend.main_library.other as m_o


TIMEOUT = 60 * 10

TIMEOUT_MESSAGE = "Command timed out. Please use the command again."


async def send_error(ctx, suffix):
    """Sends an error, but with a syntax."""
    await s_e.send_error(ctx, f"{suffix} Try again.", send_author=True)


async def wait_for_message(ctx: cmds.Context, timeout=TIMEOUT):
    """Wait for a message then return the response."""
    try:
        response: nx.Message = await vrs.global_bot.wait_for("message", check=w_f_ch.check_message(ctx), timeout=timeout)
    except asyncio.TimeoutError as exc:
        await s_e.send_error(ctx, TIMEOUT_MESSAGE)
        raise c_e.ExitFunction() from exc
    return response


class ExampleView(nx.ui.View):
    """An example view."""
    def __init__(self):
        super().__init__()
        self.value = None

    @nx.ui.button(label="one", style=nx.ButtonStyle.green)
    async def button_one(self, button: nx.ui.Button, interact: nx.Interaction):
        """Button!"""
        self.value = "one"
        self.stop()


async def wait_for_view(ctx: cmds.Context, original_message: nx.Message, view: typ.Type[nx.ui.View] | ExampleView, timeout=TIMEOUT):
    """Waits for an interaction."""
    try:
        await vrs.global_bot.wait_for("interaction", check=w_f_ch.check_interaction(ctx, original_message), timeout=timeout)
    except asyncio.TimeoutError as exc:
        await s_e.send_error(ctx, TIMEOUT_MESSAGE)
        raise c_e.ExitFunction() from exc
    return view


class OutputTypes:
    """A class containing identifiers for outputs of a message or a view."""
    message = m_o.Unique()
    view = m_o.Unique()

async def wait_for_message_view(ctx: cmds.Context, original_message: nx.Message, view: typ.Type[nx.ui.View] | ExampleView, timeout=TIMEOUT):
    """Waits for a message then returns (MessageViewCheck.message, message). If instead it was a view interaction, return (MessageViewCheck.view, view) of that interaction."""

    events = [
        vrs.global_bot.wait_for("message", check=w_f_ch.check_message(ctx)),
        vrs.global_bot.wait_for("interaction", check=w_f_ch.check_interaction(ctx, original_message))
    ]

    done, pending = await asyncio.wait(events, timeout=timeout, return_when=asyncio.FIRST_COMPLETED)

    if len(done) == 0:
        await s_e.send_error(ctx, TIMEOUT_MESSAGE)
        raise c_e.ExitFunction()

    result: asyncio.Task = done.pop()
    result = result.result()
    for task in pending:
        task: asyncio.Task = task
        task.cancel()

    if isinstance(result, nx.Message):
        return OutputTypes.message, result
    if isinstance(result, nx.Interaction):
        return OutputTypes.view, view

    raise c_e.InvalidResponse()
