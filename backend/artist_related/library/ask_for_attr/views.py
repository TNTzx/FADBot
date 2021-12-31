"""Contains a list of views to be used for asking for attributes."""

# pylint: disable=unused-argument


import nextcord as nx

import backend.main_library.views as vw


FIRST_ROW = 0
IS_LAST_ROW = 4


class ButtonCancel(vw.View):
    """Cancel button."""

    @nx.ui.button(label="Cancel", style=nx.ButtonStyle.red, row=IS_LAST_ROW)
    async def cancel(self, button: nx.ui.Button, interact: nx.Interaction):
        "...cancel!"
        self.value = True
        self.stop()

class ButtonSkipEnabled(vw.View):
    """Skip button. Enabled."""
    @nx.ui.button(label="Skip", style=nx.ButtonStyle.green, row=IS_LAST_ROW)
    async def skip_enabled(self, button: nx.ui.Button, interact: nx.Interaction):
        """skip!"""
        self.value = True
        self.stop()

class ButtonSkipDisabled(vw.View):
    """Skip button. Disabled."""
    @nx.ui.button(label="Skip", disabled=True, style=nx.ButtonStyle.green, row=IS_LAST_ROW)
    async def skip_disabled(self, button: nx.ui.Button, interact: nx.Interaction):
        """skip!"""
        self.value = True
        self.stop()


class ViewCancelOnly(ButtonCancel, ButtonSkipDisabled):
    """Cancel button only."""

class ViewCancelSkip(ButtonCancel, ButtonSkipEnabled):
    """Cancel button with skip."""


def select_option_factory(options: list[str]):
    return [nx.SelectOption(label=value) for value in options]

class SelectOptions(vw.View):
    @nx.ui.select(placeholder="AAAAA", options=select_option_factory(["a", "AAAA"]))
    async def select(self, button: nx.ui.Button, interact: nx.Interaction):
        """el"""
        return
