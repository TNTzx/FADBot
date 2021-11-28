"""Other fun functions!"""

# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods


import datetime
import nextcord as nx

import functions.exceptions.custom_exc as c_exc


class Match:
    """Structure that contains a dictionary and a value to match it with."""
    def __init__(self, data_dict: dict[int, str], value: int):
        self.data_dict = data_dict
        self.value = value

    def get_name(self):
        """Gets the name of the value."""
        return self.data_dict[self.value]

class Unique():
    """Unique variable!"""
    def __init__(self):
        pass

async def get_tntz(bot: nx.Client):
    """Gets TNTz."""
    return await bot.fetch_user(279803094722674693)


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


async def get_channel_from_mention(bot, mention: str):
    """Gets channel from a mention."""
    get_id = mention[2:-1]
    obj = bot.get_channel(int(get_id))
    return obj


def get_dict_attr(obj):
    """Gets attributes of an object then returns it as a dict."""
    dictionary = {}
    for attr, value in obj.__dict__.items():
        if not hasattr(value, '__dict__'):
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

def remove_none_in_list(_list: list):
    """Removes all instances of None in a list."""
    clean_list = []
    for item in _list:
        if item is None:
            continue
        clean_list.append(item)
    return clean_list
