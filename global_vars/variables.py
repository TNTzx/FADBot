"""Where global variables reside."""

import json
import os
import pyrebase
import nextcord as nx

# Command Prefix
CMD_PREFIX = "##"

# Bot
global_bot = nx.Client()


# Tent
TNTz: nx.User = None


# Database
env = os.environ["FadbDBToken"]
env_dict = json.loads(env)
db_key = env_dict["databaseKey"]
fb = pyrebase.initialize_app(db_key)

db = fb.database()
fbAuth = fb.auth()

envAuth = env_dict["auth"]
fb_user = fbAuth.sign_in_with_email_and_password(envAuth["email"], envAuth["password"])

def get_token():
    """Gets the token."""
    fb_token = fb_user['idToken']
    return fb_token

PLACEHOLDER_DATA = [["placeholder"]]


# API
API_LINK = "https://fadb.live/api"
API_AUTH_TOKEN = os.environ["FadbAuthToken"]
API_HEADERS = {
    "Authorization": f"Basic {API_AUTH_TOKEN}",
    "Content-Type": "application/x-www-form-urlencoded"
}


# Timeouts
class Timeouts:
    """Class that contains common timeout durations."""
    SHORT = 10
    MEDIUM = 60
    LONG = 60 * 10

