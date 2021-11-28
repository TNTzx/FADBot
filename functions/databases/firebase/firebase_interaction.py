"""Interacts with the Firebase Database."""

import collections as cl
import threading as thread

import functions.exceptions.custom_exc as c_exc
import functions.databases.firebase.firebase_reset_token as f_r_t
import global_vars.variables as vrs


def get_from_path(path: list[str]):
    """Returns the database child of a path."""
    final = vrs.db
    for key in path:
        if not isinstance(key, str):
            key = str(key)
        final = final.child(key)
    return final


def get_data(path: list[str]):
    """Gets the data."""
    result = get_from_path(path).get(token=vrs.get_token()).val()

    if not result is None:
        value = result
        if isinstance(value, cl.OrderedDict):
            value = dict(result)
        return value
    else:
        raise c_exc.FirebaseNoEntry(f"Data doesn't exist for '{path}'.")


# Check if data already exists
def is_data_exists(path: list[str]):
    """Checks if the path exists."""
    try:
        get_data(path)
        return True
    except c_exc.FirebaseNoEntry:
        return False


# Create
def override_data(path: list[str], data: dict):
    """Overrides the data at a specific path."""
    path_parse = get_from_path(path)
    path_parse.set(data, token=vrs.get_token())

# Append
def append_data(path: list[str], data: list):
    """Adds data to a specific path. Only works with lists."""
    new_data = get_data(path)
    new_data += data
    override_data(path, new_data)

# Edit
def edit_data(path: list[str], data: dict):
    """Edits data in a path. Use key-value pairs. Won't replace data in path."""
    if not is_data_exists(path):
        raise c_exc.FirebaseNoEntry(f"Data can't be found for '{path}'.")

    path_parse = get_from_path(path)
    path_parse.update(data, token=vrs.get_token())


# Delete
def delete_data(path: list[str]):
    """Deletes the path."""
    if not is_data_exists(path):
        raise c_exc.FirebaseNoEntry(f"Data being deleted doesn't exist for '{path}'.")

    path_parse = get_from_path(path)
    path_parse.remove(token=vrs.get_token())


new_token = thread.Thread(target=f_r_t.start_loop)
new_token.daemon = True
new_token.start()
