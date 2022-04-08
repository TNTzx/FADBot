"""Where global variables reside."""

import json
import os
import pyrebase
import nextcord as nx

# Command Prefix
CMD_PREFIX = "##"

# Bot
bot = nx.Client()


# Tent
TNTz: nx.User = None


# Timeouts
class Timeouts:
    """Class that contains common timeout durations."""
    short = 10
    medium = 60
    long = 60 * 10


# Colors!
COLOR_PA = 0xFFAEAE
