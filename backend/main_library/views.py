"""A module that contains a class where views will be inherited to."""

# pylint: disable=unused-argument


import nextcord as nx


class View(nx.ui.View):
    """The default view."""
    def __init__(self):
        super().__init__()
        self.value = None


def select_factory(options: list[nx.SelectOption]):
    """Creates a select class."""
    class SelectOptions(View):
        """A class for select options."""
        @nx.ui.select(placeholder="Select...", options=options)
        async def select(self, select: nx.ui.Select, interact: nx.Interaction):
            """Main select."""
            self.value = select.values
            return

    return SelectOptions
