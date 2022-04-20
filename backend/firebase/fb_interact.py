"""Interacts with the Firebase Database."""

import collections as cl
import threading as thread

import backend.logging as lgr
import backend.other as ot

from . import fb_consts as consts
from . import fb_utils
from . import fb_reset_token as f_r_t
from . import fb_exc


def get_from_path(path: list[str]):
    """Returns the database child of a path."""
    final = consts.db
    for key in path:
        if not isinstance(key, str):
            key = str(key)
        final = final.child(key)
    return final


def get_data(path: list[str], default = consts.NOT_FOUND_DATA):
    """Gets the data. Returns `default` if not found, else raise an `FBNoPath` exception."""
    default_not_overridden = default == consts.NOT_FOUND_DATA
    result = get_from_path(path).get(token = consts.get_token()).val()

    if fb_utils.placeholder_empty_to_none(result) is None:
        if default_not_overridden:
            return None

        return default


    result = fb_utils.null_placeholder_empty_to_none(result)

    if result is None:
        if default_not_overridden:
            raise fb_exc.FBNoPath(f"Data doesn't exist for '{path}', or is None.")

        return default

    if isinstance(result, cl.OrderedDict):
        result = dict(result)

    log_message = f"Received data from path {path}: {ot.pr_print(result)}"
    lgr.log_firebase.info(log_message)
    return result


def is_data_exists(path: list[str]):
    """Checks if the path exists."""
    try:
        get_data(path)
        return True
    except fb_exc.FBNoPath:
        return False


def override_data(path: list[str], json: dict):
    """Overrides the data at a specific path."""
    path_parse = get_from_path(path)

    json = fb_utils.none_empty_to_null(json)

    log_message = f"Overriden data from path {path}: {ot.pr_print(json)}"
    lgr.log_firebase.info(log_message)
    path_parse.set(json, token = consts.get_token())


def append_data(path: list[str], json: list):
    """Adds data to a specific path. Only works with lists."""
    new_data = get_data(path, default = [])
    new_data += json

    new_data = fb_utils.none_empty_to_null(new_data)

    log_message = f"Appended data from path {path}: {ot.pr_print(new_data)}"
    lgr.log_firebase.info(log_message)
    override_data(path, new_data)


def deduct_data(path: list[str], json: list):
    """Deletes data in a specific path. Only works with lists."""
    old_data = get_data(path, default = [])

    try:
        new_data = ot.subtract_list(old_data, json)
    except ValueError as exc:
        raise fb_exc.FBNoPath("Not subtracted.") from exc

    new_data = fb_utils.none_empty_to_null(new_data)

    log_message = f"Deducted data from path {path}: {ot.pr_print(new_data)}"
    lgr.log_firebase.info(log_message)
    override_data(path, new_data)


# Edit
def edit_data(path: list[str], json: dict | list):
    """Edits data in a path. Use a `dict` or a `list`. Won't replace data in path."""
    path_parse = get_from_path(path)

    if isinstance(json, list):
        json = fb_utils.list_to_dict(json)

    json = fb_utils.none_empty_to_null(json)

    log_message = f"Edited data from path {path}: {ot.pr_print(json)}"
    lgr.log_firebase.info(log_message)
    path_parse.update(json, token = consts.get_token())


# Delete
def delete_data(path: list[str]):
    """Deletes the path."""
    if not is_data_exists(path):
        raise fb_exc.FBNoPath(f"Data being deleted doesn't exist for '{path}'.")

    path_parse = get_from_path(path)

    log_message = f"Deleted data from path {path}."
    lgr.log_firebase.info(log_message)
    path_parse.remove(token = consts.get_token())


new_token = thread.Thread(target = f_r_t.start_loop)
new_token.daemon = True
new_token.start()
