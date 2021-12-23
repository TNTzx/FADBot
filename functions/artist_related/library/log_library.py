"""Log library for logging."""

# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
# pylint: disable=useless-super-delegation
# pylint: disable=unused-import
# pylint: disable=invalid-name

from __future__ import annotations
import nextcord as nx
import nextcord.ext.commands as cmds

import functions.main_classes.dataclass as dt
import functions.main_classes.message_pointer as m_p
import functions.other_functions as o_f

class LogTypes:
    """Class that contains log types."""
    class Base:
        """Base class."""
        def __init__(self):
            self.path: list[str] = None
            self.title_str: str = None

    class Pending(Base):
        """For pending artist submissions."""
        def __init__(self):
            super().__init__()
            self.path = ["artistData", "pending", "data"]
            self.title_str = "A new pending artist submission has been created."
    PENDING = Pending()

    class Editing(Base):
        """For editing requests."""
        def __init__(self):
            super().__init__()
            self.path = ["artistData", "editing", "data"]
            self.title_str = "A new edit request has been created."

    EDITING = Editing()


class LogMessages(dt.Dataclass):
    """A data structure to store messages of a log.
    "main": m_p.MessagePointer
    "proof": m_p.MessagePointer"""
    def __init__(self, datas: dict[str, m_p.MessagePointer] = None):
        if datas is None:
            datas = {
                "main": None,
                "proof": None,
            }

        self.main = m_p.MessagePointer(datas["main"])
        self.proof = m_p.MessagePointer(datas["proof"])

class Log(dt.Dataclass):
    """A data structure to store a log.
    "message": LogMessages
    "user_id": int"""
    def __init__(self, datas: dict = None):
        if datas is None:
            datas = {
                "message": None,
                "user_id": None
            }

        self.message = LogMessages(datas["message"])
        self.user_id = str(datas["user_id"])
