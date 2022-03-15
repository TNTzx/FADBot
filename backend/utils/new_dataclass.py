"""Dataclass."""


from __future__ import annotations

import abc

import requests as req


class Dataclass():
    """A dataclass."""
    def __repr__(self) -> str:
        return str(self.to_one_obj())

    def to_one_obj(self) -> list | dict:
        """Function that returns a dictionary version of the object."""
        return self.__dict__

    @classmethod
    def from_obj(cls, data: list | dict) -> None:
        """Function that takes in a dictionary then returns the object-ified version."""
        raise TypeError(f"\"{cls.__name__}\" does not implement dictionary conversion.")


class APIDataclass(Dataclass):
    """A dataclass with API support."""
    def send_data(self) -> None:
        """Sends the data."""

    def to_payload(self) -> dict | tuple | list:
        """Function that returns the payload."""
        return self.to_one_obj()

    @classmethod
    def from_response(cls, response: req.models.Response):
        """Function that returns an object-ified version of a response."""
        return cls.from_dict_response(response.json())

    @classmethod
    def from_dict_response(cls, response: dict):
        """Function that returns an object-ified version of a dictionary of a response."""
        return cls.from_obj(response)


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
