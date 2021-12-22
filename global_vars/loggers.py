"""Contains logging variables."""

# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods

import os
import logging as log


formatter = log.Formatter("[%(asctime)s | %(filename)s + %(funcName)s] [%(name)s | %(levelname)s]:   %(message)s")
logs_path = os.path.join(os.path.split(__file__)[0], "..", "logs")

def check_if_create_path(path):
    """Checks if a path exists. If it doesn't, it gets created."""
    if not os.path.isdir(path):
        os.mkdir(path)

check_if_create_path(logs_path)


def form_filename(sort_num: int, filename: str, extension=".txt"):
    """Format filenames!"""
    return f"[{sort_num}] {filename}{extension}"


def setup_file_handler(filename):
    """Make a file handler!"""
    handler = log.FileHandler(os.path.join(logs_path, filename), mode="w")
    handler.setFormatter(formatter)

    return handler

default_handle = setup_file_handler(form_filename(0, "master"))

def setup_logger(name, is_master=False, filename="", level=log.DEBUG):
    """Make a logger!"""

    logger = log.getLogger(name)
    logger.setLevel(level)

    logger.addHandler(default_handle)

    if not is_master:
        handler = setup_file_handler(filename)
        logger.addHandler(default_handle)
        logger.addHandler(handler)

    return logger


class LogPaths:
    """Contains names for folders."""
    databases = "databases"
    bot_control = "bot_control"

logger_paths = [getattr(LogPaths, x) for x in dir(LogPaths) if not x.startswith("__")]
for logger_path in logger_paths:
    check_if_create_path(os.path.join(logs_path, logger_path))


log_master = setup_logger("master", is_master=True)

log_global_exc = setup_logger("global_exc", filename=form_filename(0, "global_exc"))

log_bot_status = setup_logger("bot_status", filename=os.path.join(LogPaths.bot_control, form_filename(1, "bot_status")))

log_firebase = setup_logger("firebase", filename=os.path.join(LogPaths.databases, form_filename(1, "firebase")))
log_vadb = setup_logger("vadb", filename=os.path.join(LogPaths.databases, form_filename(1, "vadb")))
