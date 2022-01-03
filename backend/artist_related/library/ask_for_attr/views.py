"""Contains a list of views to be used for asking for attributes."""

# pylint: disable=unused-argument


import nextcord as nx

import backend.main_library.views as vw
import backend.main_library.other as m_ot


FIRST_ROW = 0
IS_LAST_ROW = 4

class OutputValues:
    """Contains output values for stuff like Cancel and Skip."""
    cancel = m_ot.Unique()
    skip = m_ot.Unique()
    confirm = m_ot.Unique()


class Blank(vw.View):
    """A blank view."""


class ButtonCancel(vw.View):
    """Cancel button."""
    @nx.ui.button(label="Cancel", style=nx.ButtonStyle.red, row=IS_LAST_ROW)
    async def cancel(self, button: nx.ui.Button, interact: nx.Interaction):
        "...cancel!"
        self.value = OutputValues.cancel
        self.stop()

class ButtonConfirm(vw.View):
    """Confirm button."""
    @nx.ui.button(label="Confirm", style=nx.ButtonStyle.green, row=IS_LAST_ROW)
    async def confirm(self, button: nx.ui.Button, interact: nx.Interaction):
        "...cancel!"
        self.value = OutputValues.confirm
        self.stop()

class ButtonSkipEnabled(vw.View):
    """Skip button. Enabled."""
    @nx.ui.button(label="Skip", style=nx.ButtonStyle.blurple, row=IS_LAST_ROW)
    async def skip_enabled(self, button: nx.ui.Button, interact: nx.Interaction):
        """skip!"""
        self.value = OutputValues.skip
        self.stop()

class ButtonSkipDisabled(vw.View):
    """Skip button. Disabled."""
    @nx.ui.button(label="Skip", disabled=True, style=nx.ButtonStyle.blurple, row=IS_LAST_ROW)
    async def skip_disabled(self, button: nx.ui.Button, interact: nx.Interaction):
        """skip!"""
        self.value = OutputValues.skip
        self.stop()


class ViewCancelOnly(ButtonCancel, ButtonSkipDisabled):
    """Cancel button only."""

class ViewCancelSkip(ButtonCancel, ButtonSkipEnabled):
    """Cancel button with skip."""

class ViewConfirmCancel(ButtonCancel, ButtonConfirm):
    """Confirm and cancel."""
