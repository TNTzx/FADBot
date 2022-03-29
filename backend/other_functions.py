"""Other fun functions!"""


import datetime

import global_vars.variables as vrs
import backend.exceptions.custom_exc as c_exc


def format_time(num: int):
    """Formats the time from seconds to '#h #m #s'."""
    seconds = num
    time = str(datetime.timedelta(seconds=seconds))
    time = time.split(":")

    time_final_list = []
    if not time[0] == "0":
        time_final_list.append(f"{int(time[0])}h")
    if not time[1] == "00":
        time_final_list.append(f"{int(time[1])}m")
    if not time[2] == "00":
        time_final_list.append(f"{int(time[2])}s")

    time_final = " ".join(time_final_list)
    if time_final == "":
        time_final = "less than a second"
    return time_final


async def get_channel_from_mention(mention: str):
    """Gets channel from a mention."""
    try:
        get_id = mention[2:-1]
    except TypeError:
        return None

    try:
        obj = vrs.global_bot.get_channel(int(get_id))
    except ValueError:
        return None

    return obj


def get_dict_attr(obj):
    """Gets attributes of an object then returns it as a dict."""
    def check_if_has_dict(obj):
        return hasattr(obj, "__dict__")

    dictionary = {}
    for attr, value in obj.__dict__.items():
        if isinstance(value, list):
            value_list = []
            for value_item in value:
                if not check_if_has_dict(value_item):
                    value_list.append(value_item)
                else:
                    value_list.append(get_dict_attr(value_item))
            dictionary[attr] = value_list
        elif not check_if_has_dict(value):
            dictionary[attr] = value
        else:
            dictionary[attr] = get_dict_attr(value)
    return dictionary


def override_dicts_recursive(default: dict, override: dict):
    """Override values of a dict with another dict."""
    new = default.copy()
    for key in override.keys():
        if key in default:
            if isinstance(default[key], dict) and isinstance(override[key], dict):
                new[key] = override_dicts_recursive(default[key], override[key])
            else:
                new[key] = override[key]
        else:
            raise c_exc.DictOverrideError(f"Key '{key}' on override dict doesn't have an entry in default dict.")

    return new

def is_not_blank_str(string: str | None):
    """Checks if a string is blank or None."""
    if string is None:
        return False
    if string.strip() == "":
        return False
    return True

def is_not_empty(variable):
    """Returns the variable if it is not None or not an empty iterable."""
    if variable is not None:
        if len(variable) != 0:
            return True
    return False

def remove_none_in_list(_list: list):
    """Removes all instances of None in a list."""
    clean_list = []
    for item in _list:
        if item is None:
            continue
        clean_list.append(item)
    return clean_list

def subtract_list(minuend: list, subtrahend: list):
    """Subtract two lists."""
    difference = [item for item in minuend if item not in subtrahend]
    if difference == minuend:
        raise ValueError("Unchanged list.")
    return difference

def get_value_from_key(diction: dict, value):
    """Get the key using a value. INVERSE DICTIONARY!!!!!!!!"""
    return list(diction.keys())[list(diction.values()).index(value)]


def pr_print(value, htchar='\t', lfchar='\n', indent=0):
    """Returns a string for pretty logging."""
    nlch = lfchar + htchar * (indent + 1)
    if isinstance(value, dict):
        items = [
            nlch + repr(key) + ': ' + pr_print(value[key], htchar, lfchar, indent + 1)
            for key in value
        ]
        return '{%s}' % (','.join(items) + lfchar + htchar * indent)
    if isinstance(value, list):
        items = [
            nlch + pr_print(item, htchar, lfchar, indent + 1)
            for item in value
        ]
        return '[%s]' % (','.join(items) + lfchar + htchar * indent)
    if isinstance(value, tuple):
        items = [
            nlch + pr_print(item, htchar, lfchar, indent + 1)
            for item in value
        ]
        return '(%s)' % (','.join(items) + lfchar + htchar * indent)

    return repr(value)
