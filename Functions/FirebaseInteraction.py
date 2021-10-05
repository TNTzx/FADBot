import collections as cl
import os
import json

import pyrebase
import threading as thread

from Functions import CustomExceptions as ce
from Functions import FirebaseResetToken as frt
from GlobalVariables import variables as vars


# Get data from keys in database
def getFromPath(path):
    final = vars.db
    for key in path:
        if not isinstance(key, str):
            key = str(key)
        final = final.child(key)
    return final


# Get Data
def getData(path:list):
    result = getFromPath(path).get(token=vars.getToken()).val()
    
    if not result == None:
        value = result
        if isinstance(value, cl.OrderedDict):
            value = dict(result)
        return value
    else:
        raise ce.FirebaseNoEntry(f"Data doesn't exist for '{path}'.")
    

# Check if data already exists
def isDataExists(path):
    try:
        getData(path)
        return True
    except ce.FirebaseNoEntry:
        return False


# Create
def createData(path, data):
    pathParse = getFromPath(path)
    pathParse.set(data, token=vars.getToken())

# Edit
def editData(path, data):
    if not isDataExists(path):
        raise ce.FirebaseNoEntry(f"Data can't be found for '{path}'.")

    pathParse = getFromPath(path)
    pathParse.update(data, token=vars.getToken())


# Delete
def deleteData(path):
    if not isDataExists(path):
        raise ce.FirebaseNoEntry(f"Data being deleted doesn't exist for '{path}'.")
    
    pathParse = getFromPath(path)
    pathParse.remove(token=vars.getToken())


newToken = thread.Thread(target=frt.startLoop)
newToken.daemon = True
newToken.start()