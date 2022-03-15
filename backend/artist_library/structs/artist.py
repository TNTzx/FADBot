"""Contains logic for storing artists."""


from __future__ import annotations

import tldextract as tld

import backend.utils.new_dataclass as dt
import backend.utils.other as util_other


from .struct_exts import states as st
from .struct_exts import image_info as img


class Artist(dt.MainDataclass):
    """An artist."""
    def __init__(
            self,
            name: str | None = None,
            proof: str = DEFAULT_IMAGE,
            vadb_info: VADBInfo = VADBInfo(),
            states: States = States(),
            details: Details = Details()
            ):
        self.name = name
        self.proof = proof
        self.vadb_info = vadb_info
        self.states = states
        self.details = details


    def vadb_create(self):
        """Creates the artist on VADB."""

    @classmethod
    def from_sub(
            cls,
            data: dt.SubDataclass
            ) -> None:
        pass
