"""Contains a list of views to be used for asking for attributes."""

# pylint: disable=unused-argument


import nextcord as nx

import backend.main_library.views as vw


class Cancel(vw.View):
    """Cancel button."""

    @nx.ui.button(label="Cancel", style=nx.ButtonStyle.red)
    def cancel(self, button: nx.ui.Button, interact: nx.Interaction):
        "...cancel!"
        self.value = True
        self.stop()
