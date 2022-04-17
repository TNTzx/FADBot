"""Module that contains the function to reset the token."""


import time
# import datetime
# import pytz

import backend.logging as lgr

from . import fb_consts


def start_loop():
    """Starts the loop to reset the token periodically."""
    while True:
        time.sleep(60 * 30)
        fb_consts.fb_user = fb_consts.fb_auth.refresh(fb_consts.fb_user['refreshToken'])

        # timezone = pytz.timezone('Asia/Manila')
        # time_obj = datetime.datetime.now(timezone)
        # time_str = time_obj.strftime("%I:%M:%S %p | %a, %d/%m/%Y")

        lgr.log_firebase.info("Token reset.")
