"""Interacts with the Firebase Database."""

import collections as cl
import threading as thread

from Functions import CustomExceptions as ce
from Functions import FirebaseResetToken as frt
from GlobalVariables import variables as varss


def get_from_path(path: list[str]):
    """Returns the database child of a path."""
    final = varss.db
    for key in path:
        if not isinstance(key, str):
            key = str(key)
        final = final.child(key)
    return final


def get_data(path: list[str]):
    """Gets the data."""
    result = get_from_path(path).get(token=varss.get_token()).val()

    if not result is None:
        value = result
        if isinstance(value, cl.OrderedDict):
            value = dict(result)
        return value
    else:
        raise ce.FirebaseNoEntry(f"Data doesn't exist for '{path}'.")


# Check if data already exists
def is_data_exists(path: list[str]):
    """Checks if the path exists."""
    try:
        get_data(path)
        return True
    except ce.FirebaseNoEntry:
        return False


# Create
def create_data(path: list[str], data):
    """Overrides the data at a specific path."""
    path_parse = get_from_path(path)
    path_parse.set(data, token=varss.get_token())

# Append
def append_data(path: list[str], data: list):
    """Adds data to a specific path. Only works with lists."""
    new_data = get_data(path)
    new_data += data
    create_data(path, new_data)

# Edit
def edit_data(path: list[str], data):
    """Changes / overrides data in a path."""
    if not is_data_exists(path):
        raise ce.FirebaseNoEntry(f"Data can't be found for '{path}'.")

    path_parse = get_from_path(path)
    path_parse.update(data, token=varss.get_token())


# Delete
def delete_data(path):
    """Deletes the path."""
    if not is_data_exists(path):
        raise ce.FirebaseNoEntry(f"Data being deleted doesn't exist for '{path}'.")

    path_parse = get_from_path(path)
    path_parse.remove(token=varss.get_token())


new_token = thread.Thread(target=frt.start_loop)
new_token.daemon = True
new_token.start()
