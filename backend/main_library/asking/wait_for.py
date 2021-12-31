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


async def send_error(ctx, suffix):
    """Sends an error, but with a syntax."""
    await s_e.send_error(ctx, f"{suffix} Try again.", send_author=True)

async def wait_for_response(ctx: cmds.Context, timeout=TIMEOUT):
    """Wait for a message then return the response."""
    try:
        response: nx.Message = await vrs.global_bot.wait_for("message", check=w_f_ch.check_message(ctx), timeout=timeout)

    except asyncio.TimeoutError as exc:
        await s_e.send_error(ctx, "Command timed out. Please use the command again.")
        raise c_e.ExitFunction("Exited Function.") from exc
    return response


class ExampleView(nx.ui.View):
    """An example view."""
    def __init__(self):
        super().__init__()
        self.value = None
    
    @nx.ui.button(label="one", style=nx.ButtonStyle.green)
    async def button_one(self, button: nx.ui.Button, interact: nx.Interaction):
        self.value = "one"
        self.stop()


class MessageViewCheck:
    """A class containing identifiers for outputs of a message or a view."""
    message = m_o.Unique()
    view = m_o.Unique()

async def wait_for_response_view(ctx: cmds.Context, original_message: nx.Message, view: typ.Type[nx.ui.View] | ExampleView, timeout=TIMEOUT):
    """Waits for a message then returns that message. If instead it was a view interaction, return the value of that interaction."""

    events = [
        vrs.global_bot.wait_for("message", check=w_f_ch.check_message(ctx)),
        vrs.global_bot.wait_for("interaction", check=w_f_ch.check_interaction(ctx, original_message))
    ]

    done, pending = await asyncio.wait(events, return_when=asyncio.FIRST_COMPLETED)

    result: asyncio.Task = done.pop()
    result = result.result()
    for task in pending:
        task: asyncio.Task = task
        task.cancel()
    
    if isinstance(result, nx.Message):
        return MessageViewCheck.message, result
    elif isinstance(result, nx.Interaction):
        return MessageViewCheck.view, view.value
