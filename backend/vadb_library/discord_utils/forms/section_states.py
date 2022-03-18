"""Contains section states such as skippable and editing."""


import typing as typ

import backend.utils.views as vw


class SectionState():
    """A section state."""
    def __init__(self, name: str | None, view_cls: typ.Type[vw.View], footer: str):
        self.name = name
        self.view_cls = view_cls
        self.footer = footer


class SectionStates():
    """Section states."""
    default = SectionState(
        name = None,
        view_cls = vw.ViewCancelOnly,
        footer = (
            "Click on the \"Cancel\" button to cancel the current command."
        )
    )
    skippable = SectionState(
        name = "skippable",
        view_cls = vw.ViewCancelSkip,
        footer = (
            "Click on the \"Skip\" button to skip this section.\n"
            "Click on the \"Cancel\" button to cancel the current command."
        )
    )

    editing = SectionState(
        name = "editing",
        view_cls = vw.ViewBackCancel,
        footer = (
            "Click on the \"Back\" button to go back to the generated embed."
            "Click on the \"Cancel\" button to cancel the current command."
        )
    )
