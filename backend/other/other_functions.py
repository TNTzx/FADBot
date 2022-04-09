"""Other fun functions!"""


import datetime


# REWRITE separate to different files

def format_time(num: int):
    """Formats the time from seconds to '#h #m #s'."""
    seconds = num
    time = str(datetime.timedelta(seconds = seconds))
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


def subtract_list(minuend: list, subtrahend: list):
    """Subtract two lists."""
    difference = [item for item in minuend if item not in subtrahend]
    if difference == minuend:
        raise ValueError("Unchanged list.")
    return difference


def pr_print(value, htchar = '\t', lfchar = '\n', indent = 0):
    """Returns a string for pretty logging."""
    nlch = lfchar + htchar * (indent + 1)
    if isinstance(value, dict):
        items = [
            nlch + repr(key) + ": " + pr_print(value[key], htchar, lfchar, indent + 1)
            for key in value
        ]
        return ",".join(items) + lfchar + htchar * indent
    if isinstance(value, list):
        items = [
            nlch + pr_print(item, htchar, lfchar, indent + 1)
            for item in value
        ]
        return ",".join(items) + lfchar + htchar * indent
    if isinstance(value, tuple):
        items = [
            nlch + pr_print(item, htchar, lfchar, indent + 1)
            for item in value
        ]
        return ",".join(items) + lfchar + htchar * indent

    return repr(value)
