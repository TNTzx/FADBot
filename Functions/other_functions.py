"""Other fun functions!"""

import datetime

import main

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
    get_id = mention[2:-1]
    obj = main.bot.get_channel(int(get_id))
    return obj
