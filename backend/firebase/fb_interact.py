"""Interacts with the Firebase Database."""

import collections as cl
import threading as thread

import backend.logging.loggers as lgr
import backend.exceptions.custom_exc as c_exc
import backend.other_functions as o_f

from . import fb_consts as consts
from . import fb_undef_conv as undef_conv
from . import firebase_reset_token as f_r_t


def get_from_path(path: list[str]):
    """Returns the database child of a path."""
    final = consts.db
    for key in path:
        if not isinstance(key, str):
            key = str(key)
        final = final.child(key)
    return final


def get_data(path: list[str]):
    """Gets the data."""
    result = get_from_path(path).get(token = consts.get_token()).val()
    if result is None:
        raise c_exc.FirebaseNoEntry(f"Data doesn't exist for '{path}'.")

    json = result
    if isinstance(json, cl.OrderedDict):
        json = dict(result)

    json = undef_conv.null_and_empty_to_none(json)

    log_message = f"Received data from path {path}: {o_f.pr_print(json)}"
    lgr.log_firebase.info(log_message)
    return json


# Check if data already exists
def is_data_exists(path: list[str]):
    """Checks if the path exists."""
    try:
        get_data(path)
        return True
    except c_exc.FirebaseNoEntry:
        return False


# Create
def override_data(path: list[str], json: dict):
    """Overrides the data at a specific path."""
    path_parse = get_from_path(path)

    json = undef_conv.none_and_empty_to_null(json)

    log_message = f"Overriden data from path {path}: {o_f.pr_print(json)}"
    lgr.log_firebase.info(log_message)
    path_parse.set(json, token = consts.get_token())


# Append
def append_data(path: list[str], json: list):
    """Adds data to a specific path. Only works with lists."""
    new_data = get_data(path)
    new_data += json

    new_data = undef_conv.none_and_empty_to_null(new_data)

    log_message = f"Appended data from path {path}: {o_f.pr_print(new_data)}"
    lgr.log_firebase.info(log_message)
    override_data(path, new_data)


def deduct_data(path: list[str], json: list):
    """Deletes data in a specific path. Only works with lists."""
    old_data = get_data(path)

    try:
        new_data = o_f.subtract_list(old_data, json)
    except ValueError as exc:
        raise c_exc.FirebaseNoEntry("Not subtracted.") from exc

    new_data = undef_conv.none_and_empty_to_null(new_data)

    log_message = f"Deducted data from path {path}: {o_f.pr_print(new_data)}"
    lgr.log_firebase.info(log_message)
    override_data(path, new_data)


# Edit
def edit_data(path: list[str], json: dict):
    """Edits data in a path. Use key-value pairs. Won't replace data in path."""
    if not is_data_exists(path):
        raise c_exc.FirebaseNoEntry(f"Data can't be found for '{path}'.")

    path_parse = get_from_path(path)

    json = undef_conv.none_and_empty_to_null(json)

    log_message = f"Edited data from path {path}: {o_f.pr_print(json)}"
    lgr.log_firebase.info(log_message)
    path_parse.update(json, token = consts.get_token())


# Delete
def delete_data(path: list[str]):
    """Deletes the path."""
    if not is_data_exists(path):
        raise c_exc.FirebaseNoEntry(f"Data being deleted doesn't exist for '{path}'.")

    path_parse = get_from_path(path)

    log_message = f"Deleted data from path {path}."
    lgr.log_firebase.info(log_message)
    path_parse.remove(token = consts.get_token())


new_token = thread.Thread(target=f_r_t.start_loop)
new_token.daemon = True
new_token.start()
