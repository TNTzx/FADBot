"""Dataclass."""


from __future__ import annotations

import abc


class Dataclass():
    """A dataclass."""

    def to_dict(self) -> dict:
        """Function that returns a dictionary version of the object."""

    @classmethod
    def from_dict(cls, data: dict) -> None:
        """Function that takes in a dictionary then returns the object-ified version."""
        raise TypeError(f"\"{cls.__name__}\" does not implement dictionary conversion.")


class APIDataclass(Dataclass):
    """A dataclass with API support."""
    def to_payload(self) -> dict | tuple | list:
        """Function that returns the payload."""
        return self.to_dict()

    @classmethod
    def from_response(cls, data: dict):
        """Function that returns an object-ified version of a dict."""
        return cls.from_dict(data)


class DataclassConvertible(Dataclass):
    """Parent class for dataclasses that can be converted to."""


class MainDataclass(abc.ABC, DataclassConvertible):
    """A dataclass being the medium for conversions."""

    @classmethod
    @abc.abstractmethod
    def from_sub(cls, data: SubDataclass) -> None:
        """Function that takes in an instance of a SubDataclass and returns the converted MainDataclass."""


class SubDataclass(abc.ABC, DataclassConvertible):
    """A dataclass being converted to or from."""

    @classmethod
    @abc.abstractmethod
    def from_main(cls, data: MainDataclass) -> None:
        """Function that takes in an instance of a MainDataclass and returns the converted SubDataclass."""
