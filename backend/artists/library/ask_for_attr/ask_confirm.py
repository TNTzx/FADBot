"""Module that contains asking for confirmation."""

# pylint: disable=line-too-long


import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import backend.utils.views as vw
import backend.utils.asking.wait_for as w_f


TIMEOUT = vrs.Timeouts.medium

async def ask_confirm(ctx: cmds.Context):
    """Asks to confirm an action."""
    view = vw.ViewSubmitCancel()

    embed = nx.Embed(
        color = 0xFFFF00,
        title = "Confirm sending request",
        description = (
            "Are you sure you want to submit this `request` for approval?\n"
            "Please double check if the artist information is correct before submitting!\n\n"
            "Click `Submit` to submit this `request`.\n"
            "Click `Cancel` to return to editing."
        )
    )

    message = await ctx.author.send(embed=embed, view=view)

    new_view = await w_f.wait_for_view(ctx, message, view, timeout=TIMEOUT)

    if new_view.value == vw.OutputValues.submit:
        return True
    if new_view.value == vw.OutputValues.cancel:
        return False

    raise ValueError("Value not found.")
