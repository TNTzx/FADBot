"""Contains logging variables."""

# pylint: disable=line-too-long

import os
import logging as log


formatter = log.Formatter("[%(asctime)s | %(filename)s + %(funcName)s] [%(levelname)s]:   %(message)s")
logs_path = os.path.join(os.path.split(__file__)[0], "..", "logs")

if not os.path.isdir(logs_path):
    os.mkdir(logs_path)


def setup_file_handler(filename):
    """Make a file handler!"""
    handler = log.FileHandler(os.path.join(logs_path, filename))
    handler.setFormatter(formatter)

    return handler

default_handle = setup_file_handler("[0] master.txt")


def setup_logger(name, is_master=True, filename="", level=log.DEBUG):
    """Make a logger!"""

    logger = log.getLogger(name)
    logger.setLevel(level)

    if is_master:
        logger.addHandler(default_handle)
    else:
        handler = setup_file_handler(filename)
        logger.addHandler(default_handle)
        logger.addHandler(handler)

    return logger

log_master = setup_logger("master", is_master=True)
log_vadb = setup_logger("aaa", filename="[1] vadb.txt")
