"""Module that contains asking for confirmation."""

# pylint: disable=line-too-long


import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import backend.main_library.views as vw
import backend.main_library.asking.wait_for as w_f


TIMEOUT = vrs.Timeouts.MEDIUM

async def ask_confirm(ctx: cmds.Context):
    """Asks to confirm an action."""
    view = vw.ViewConfirmCancel()

    message = await ctx.author.send("Are you sure you want to submit this `request` for approval?", view=view)

    new_view = await w_f.wait_for_view(ctx, message, view, timeout=TIMEOUT)

    if new_view.value == vw.OutputValues.confirm:
        return True
    elif new_view.value == vw.OutputValues.cancel:
        return False
    else:
        raise ValueError("Value not found.")
