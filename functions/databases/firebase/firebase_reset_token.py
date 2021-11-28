"""Module that contains the function to reset the token."""

import time
import datetime
import pytz

import global_vars.variables as vrs


def start_loop():
    """Starts the loop to reset the token periodically."""
    while True:
        time.sleep(60 * 30)
        vrs.fb_user = vrs.fbAuth.refresh(vrs.fb_user['refreshToken'])

        timezone = pytz.timezone('Asia/Manila')
        time_obj = datetime.datetime.now(timezone)
        time_str = time_obj.strftime("%I:%M:%S %p | %a, %d/%m/%Y")

        print(f"Token refreshed at {time_str}.")
        