"""Library for states."""


from __future__ import annotations

import nextcord as nx

import backend.utils.new_dataclass as dt
import backend.utils.other as util_other

from . import usage_rights as u_r


class State(dt.Dataclass):
    """Parent class for states."""
    def __init__(self, label: str, value: int, choice_info: ChoiceInfo = None):
        self.label = label
        self.value = value

        if choice_info is None:
            choice_info = ChoiceInfo()
        self.choice_info = choice_info

    def get_option(self):
        """Gets the nx.SelectOption object."""
        return nx.SelectOption(
            label = self.label,
            description = self.choice_info.description,
            emoji = self.choice_info.emoji
        )

class ChoiceInfo(dt.Dataclass):
    """Info for choices in views."""
    def __init__(self, description: str = "No description", emoji: str = None) -> None:
        self.description = description
        self.emoji = emoji


class Status(State):
    """A status value."""

class Availability(State):
    """An availability value."""


class StateList():
    """A class for a list of states."""
    state_list: list[State] = []

    @classmethod
    def get_states_dict(cls):
        """Returns the list of states."""
        return {state.value: state.label for state in cls.state_list}


class StatusList(StateList):
    """Contains the status list."""
    state_list = [
        Status(
            label = "Completed",
            value = 0,
            choice_info = ChoiceInfo(
                description = "The verification process is complete for this artist.",
                emoji = "✅"
            )
        ),
        Status(
            label = "No Contact",
            value = 1,
            choice_info = ChoiceInfo(
                description = "The artist cannot be contacted.",
                emoji = "❌"
            )
        ),
        Status(
            label = "Pending",
            value = 2,
            choice_info = ChoiceInfo(
                description = "The verification process for this artist is awaiting approval.",
                emoji = "❔"
            )
        ),
        Status(
            label = "Requested",
            value = 3,
            choice_info = ChoiceInfo(
                description = "The artist is being requested to be contacted.",
                emoji = "❓"
            )
        )
    ]


class AvailabilityList(StateList):
    """Contains the availability list."""
    state_list = [
        Availability(
            label = "Verified",
            value = 0,
            choice_info = ChoiceInfo(
                description = "The artist's music is allowed to be used.",
                emoji = "✅"
            )
        ),
        Availability(
            label = "Disallowed",
            value = 1,
            choice_info = ChoiceInfo(
                description = "The artist's music is not allowed to be used.",
                emoji = "❌"
            )
        ),
        Availability(
            label = "Contact Required",
            value = 2,
            choice_info = ChoiceInfo(
                description = "The artist's music is not allowed for use until further notice.",
                emoji = "❓"
            )
        ),
        Availability(
            label = "Varies",
            value = 3,
            choice_info = ChoiceInfo(
                description = "The artist's music rights are dependent on a few conditions.",
                emoji = "❔"
            )
        ),
    ]


class States(dt.Dataclass):
    """States."""
    def __init__(
            self,
            status: int = 2,
            availability: int = 2,
            usage_rights: u_r.UsageRights = u_r.UsageRights()
            ):
        self.status = util_other.Match(StateList.get_states_dict(), status)
        self.availability = util_other.Match(AvailabilityList.get_states_dict(), availability)

        self.usage_rights = usage_rights
