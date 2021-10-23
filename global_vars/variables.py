"""Where global variables reside."""

import json
import os
import pyrebase


# Database
env = os.environ["FadbDBToken"]
envDict = json.loads(env)
db_key = envDict["databaseKey"]
fb = pyrebase.initialize_app(db_key)

db = fb.database()
fbAuth = fb.auth()

envAuth = envDict["auth"]
fb_user = fbAuth.sign_in_with_email_and_password(envAuth["email"], envAuth["password"])

def get_token():
    """Gets the token."""
    fb_token = fb_user['idToken']
    return fb_token


# API
API_LINK = "https://fadb.live/api"
API_AUTH_TOKEN = os.environ["FadbAuthToken"]
API_HEADERS = {
  "Authorization": f"Basic {API_AUTH_TOKEN}",
  "Content-Type": "application/x-www-form-urlencoded"
}


# # Authorization
# canVerify = {
#   "servers": {
#     734204348665692181: [
#       886608688318656552
#     ]
#   },
#   "users": [
#     279803094722674693
#   ]
# }


# Where to send
sendLogs = [
    {
      "server": 734204348665692181,
      "channel": 897014835945046066
  }, {
    "server": 896753662477615114,
    "channel": 897014931130576936
  }
]
