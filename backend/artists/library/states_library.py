"""Library for states."""

# pylint: disable = line-too-long


import nextcord as nx

import backend.other.dataclass as dt


class State(dt.Dataclass):
    """Parent class for states."""
    def __init__(self, data = None):
        super().__init__()
        self.label = None
        self.value = None
        self.choice_info = self.ChoiceInfo()

    class ChoiceInfo(dt.DataclassSub):
        """Info for choices in views."""
        def __init__(self) -> None:
            super().__init__()
            self.description = None
            self.emoji = None

    def get_option(self):
        """Gets the nx.SelectOption object."""
        return nx.SelectOption(
            label = self.label,
            description = self.choice_info.description,
            emoji = self.choice_info.emoji
        )

class Status(State):
    """A status value."""

class Availability(State):
    """An availability value."""


status_list = [
    Status().from_dict({
        "label": "Completed",
        "value": 0,
        "choice_info": {
            "description": "The verification process is complete for this artist.",
            "emoji": "✅"
        }
    }),
    Status().from_dict({
        "label": "No Contact",
        "value": 1,
        "choice_info": {
            "description": "The artist cannot be contacted.",
            "emoji": "❌"
        }
    }),
    Status().from_dict({
        "label": "Pending",
        "value": 2,
        "choice_info": {
            "description": "The verification process for this artist is awaiting approval.",
            "emoji": "❔"
        }
    }),
    Status().from_dict({
        "label": "Requested",
        "value": 3,
        "choice_info": {
            "description": "The artist is being requested to be contacted.",
            "emoji": "❓"
        }
    })
]

availability_list = [
    Availability().from_dict({
        "label": "Verified",
        "value": 0,
        "choice_info": {
            "description": "The artist's music is allowed to be used.",
            "emoji": "✅"
        }
    }),
    Availability().from_dict({
        "label": "Disallowed",
        "value": 1,
        "choice_info": {
            "description": "The artist's music is not allowed to be used.",
            "emoji": "❌"
        }
    }),
    Availability().from_dict({
        "label": "Contact Required",
        "value": 2,
        "choice_info": {
            "description": "The artist's music is not allowed for use until further notice.",
            "emoji": "❓"
        }
    }),
    Availability().from_dict({
        "label": "Varies",
        "value": 3,
        "choice_info": {
            "description": "The artist's music rights are dependent on a few conditions.",
            "emoji": "❔"
        }
    }),
]
