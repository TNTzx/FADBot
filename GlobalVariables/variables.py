import json, os
import pyrebase


# Initialize database
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