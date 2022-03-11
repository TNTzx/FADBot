"""Library for states."""


from __future__ import annotations

import nextcord as nx

import backend.utils.new_dataclass as dt


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

class ChoiceInfo(dt.DataclassSub):
    """Info for choices in views."""
    def __init__(self, description: str, emoji: str = None) -> None:
        self.description = description
        self.emoji = emoji


class Status(State):
    """A status value."""

class Availability(State):
    """An availability value."""


class StateList():
    """A class for a list of states."""
    state_list: list[State] = None

    @classmethod
    def get_states_dict(cls):
        """Returns the list of states."""
        return {status.value: status.label for status in cls.state_list}


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
