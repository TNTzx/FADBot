import json, os
import pyrebase

# Admin Role
adminRole = "///Moderator"

# Database
env = os.environ["FadbDBToken"]
envDict = json.loads(env)
dbKey = envDict["databaseKey"]
fb = pyrebase.initialize_app(dbKey)

db = fb.database()
fbAuth = fb.auth()

envAuth = envDict["auth"]
fbUser = fbAuth.sign_in_with_email_and_password(envAuth["email"], envAuth["password"])

def getToken():
    fbToken = fbUser['idToken']
    return fbToken


# API

apiLink = "https://fadb.live/"
apiAuthToken = os.environ["FadbAuthToken"]
apiHeaders = {
  "Authorization": f"Basic {apiAuthToken}",
  "Content-Type": "application/x-www-form-urlencoded"
}