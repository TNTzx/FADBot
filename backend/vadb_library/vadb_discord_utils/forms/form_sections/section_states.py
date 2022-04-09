"""Contains section states such as skippable and editing."""


import typing as typ

import backend.discord_utils as disc_utils


class SectionState():
    """A section state."""
    def __init__(self, name: str | None, view_cls: typ.Type[disc_utils.View], footer: str):
        self.name = name
        self.view_cls = view_cls
        self.footer = footer


class SectionStates():
    """Section states."""
    default = SectionState(
        name = None,
        view_cls = disc_utils.ViewCancelOnly,
        footer = (
            "Click on the \"Cancel\" button to cancel the current command."
        )
    )
    skippable = SectionState(
        name = "skippable",
        view_cls = disc_utils.ViewCancelSkip,
        footer = (
            "Click on the \"Skip\" button to skip this section.\n"
            "Click on the \"Cancel\" button to cancel the current command."
        )
    )

    editing = SectionState(
        name = "editing",
        view_cls = disc_utils.ViewBackCancel,
        footer = (
            "Click on the \"Back\" button to go back and edit another attribute.\n"
            "Click on the \"Cancel\" button to cancel the current command."
        )
    )
