"""A module that contains a class where views will be inherited to."""


import nextcord as nx

import backend.other.other as m_ot


class View(nx.ui.View):
    """The default view."""
    def __init__(self):
        super().__init__()
        self.value = None


def select_factory(options: list[nx.SelectOption]):
    """Creates a select class."""
    class SelectOptions(View):
        """A class for select options."""
        @nx.ui.select(placeholder = "Select...", options = options)
        async def select(self, select: nx.ui.Select, interact: nx.Interaction):
            """Main select."""
            self.value = select.values
            return

    return SelectOptions



FIRST_ROW = 0
IS_LAST_ROW = 4

class OutputValues:
    """Contains output values for stuff like Cancel and Skip."""
    cancel = m_ot.Unique()
    skip = m_ot.Unique()
    confirm = m_ot.Unique()
    submit = m_ot.Unique()
    back = m_ot.Unique()


class Blank(View):
    """A blank view."""


class ButtonCancel(View):
    """Cancel button."""
    @nx.ui.button(label = "Cancel", style = nx.ButtonStyle.red, row = IS_LAST_ROW)
    async def cancel(self, button: nx.ui.Button, interact: nx.Interaction):
        "...cancel!"
        self.value = OutputValues.cancel
        self.stop()

class ButtonConfirm(View):
    """Confirm button."""
    @nx.ui.button(label = "Confirm", style = nx.ButtonStyle.green, row = IS_LAST_ROW)
    async def confirm(self, button: nx.ui.Button, interact: nx.Interaction):
        "...confirm!"
        self.value = OutputValues.confirm
        self.stop()

class ButtonSubmit(View):
    """Submit button."""
    @nx.ui.button(label = "Submit", style = nx.ButtonStyle.green, row = IS_LAST_ROW)
    async def confirm(self, button: nx.ui.Button, interact: nx.Interaction):
        "...submit!"
        self.value = OutputValues.submit
        self.stop()

class ButtonSkipEnabled(View):
    """Skip button. Enabled."""
    @nx.ui.button(label = "Skip", style = nx.ButtonStyle.blurple, row = IS_LAST_ROW)
    async def skip_enabled(self, button: nx.ui.Button, interact: nx.Interaction):
        """skip!"""
        self.value = OutputValues.skip
        self.stop()

class ButtonSkipDisabled(View):
    """Skip button. Disabled."""
    @nx.ui.button(label = "Skip", disabled = True, style = nx.ButtonStyle.blurple, row = IS_LAST_ROW)
    async def skip_disabled(self, button: nx.ui.Button, interact: nx.Interaction):
        """skip!"""
        self.value = OutputValues.skip
        self.stop()

class ButtonBack(View):
    """Back button."""
    @nx.ui.button(label = "Back", style = nx.ButtonStyle.blurple, row = IS_LAST_ROW)
    async def back(self, button: nx.ui.Button, interact: nx.Interaction):
        """back!"""
        self.value = OutputValues.back
        self.stop()


class ViewCancelOnly(ButtonCancel, ButtonSkipDisabled):
    """Cancel button only."""

class ViewCancelSkip(ButtonCancel, ButtonSkipEnabled):
    """Cancel button with skip."""

class ViewConfirmCancel(ButtonCancel, ButtonConfirm):
    """Confirm and cancel."""

class ViewSubmitCancel(ButtonCancel, ButtonSubmit):
    """Submit and cancel."""

class ViewBackCancel(ButtonCancel, ButtonBack):
    """Back and cancel."""

class ViewConfirmBackCancel(ButtonCancel, ButtonBack, ButtonConfirm):
    """Confirm, back, and cancel."""
