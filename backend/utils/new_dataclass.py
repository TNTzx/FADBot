"""Dataclass."""


from __future__ import annotations

import typing as typ
import abc


class Dataclass():
    """A dataclass."""

    def to_dict(self):
        """Function that returns a dictionary version of the object."""

    @classmethod
    def from_dict(cls, data: dict):
        """Function that takes in a dictionary then returns the object-ified version."""
        raise TypeError(f"\"{cls.__name__}\" does not implement dictionary conversion.")


class DataclassConvertible(Dataclass):
    """Parent class for dataclasses that can be converted to."""


class MainDataclass(abc.ABC, DataclassConvertible):
    """A dataclass being the medium for conversions."""

    @classmethod
    @abc.abstractmethod
    def from_sub(cls, data: SubDataclass):
        """Function that takes in an instance of a SubDataclass and returns the converted MainDataclass."""


class SetMainDataclass():
    """Sets the main dataclass."""
    def __init__(self, main_dataclass: type):
        self.main_dataclass = main_dataclass

    def __call__(self, cls: SubDataclass):
        class HasMainSubDataclass(cls):
            """A dataclass being converted to or from."""
            _main_dataclass = self.main_dataclass

        return HasMainSubDataclass


class SubDataclass(abc.ABC, DataclassConvertible):
    """A dataclass being converted to or from. Make sure to have the @SetMainDataclass() decorator set up."""

    _main_dataclass: typ.Type[MainDataclass] = None

    @classmethod
    @abc.abstractmethod
    def from_main(cls, data: MainDataclass):
        """Function that takes in an instance of a MainDataclass and returns the converted SubDataclass."""
