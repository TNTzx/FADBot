"""A module that contains a class where views will be inherited to."""

import nextcord as nx


class View(nx.ui.View):
    """The default view."""
    def __init__(self):
        super().__init__()
        self.value = None
