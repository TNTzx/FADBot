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
    class Pending:
        """For pending artist submissions."""
        def __init__(self):
            self.path = ["artistData", "pending", "data"]
            self.title_str = "A new pending artist submission has been created."
    PENDING = Pending()

    class Editing:
        """For editing requests."""
        def __init__(self):
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
                "main": o_f.MessagePointer(),
                "proof": o_f.MessagePointer(),
            }

        self.main = datas["main"]
        self.proof = datas["proof"]

class Log(o_f.DataStructure):
    """A data structure to store a log.
    "message": LogMessages
    "user_id": int"""
    def __init__(self, datas: dict[str, o_f.MessagePointer] = None):
        if datas is None:
            datas = {
                "message": LogMessages(),
                "user_id": 0
            }

        self.message = datas["message"]
        self.user_id = datas["user_id"]
