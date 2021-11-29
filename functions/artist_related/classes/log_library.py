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

import global_vars.variables as vrs
import functions.artist_related.classes.artist_library as a_l
import functions.databases.firebase.firebase_interaction as f_i
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
            self.path = ["artistData", "pending", "data"]
            self.title_str = "A new edit request has been created."

    EDITING = Editing()

class LogMessages(o_f.DataStructure):
    """A data structure to store messages of a log.
    "main": o_f.MessagePointer
    "proof": o_f.MessagePointer"""
    def __init__(self, datas: dict[str, o_f.MessagePointer] = None):
        if datas is None:
            datas = {
                "main": None,
                "proof": None,
            }

        self.main = o_f.MessagePointer(datas["main"])
        self.proof = o_f.MessagePointer(datas["proof"])

class Log(o_f.DataStructure):
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
