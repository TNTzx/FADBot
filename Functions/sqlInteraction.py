import sqlite3
import os

import json

from Functions import customExceptions as ce


cxn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "..", "Database", "database.db"))
crsr = cxn.cursor()

crsr.execute("""
    CREATE TABLE IF NOT EXISTS database (
        `artist` TEXT
        `artist_data` TEXT
)
""")

# Check for stuff like quotes
listOfReplaces = {
    "\'": "(singlequote)"
}

def redump(dictionary):
    dumped = json.dumps(dictionary)

    iterate = dumped
    for target, replace in listOfReplaces.items():
        iterate = iterate.replace(target, replace)
    
    return iterate

def undump(string):
    iterate = string
    for target, replace in listOfReplaces.items():
        iterate = iterate.replace(replace, target)
    
    undumped = json.loads(iterate)
    return undumped


# Get Data
def getData(artist, column, type=str):
    crsr.execute(f"""
    SELECT {column} FROM database
    WHERE guild_id = '{artist}'
    """)

    fetched = crsr.fetchone()
    try:
        data = fetched[0]
    except TypeError:
        return None

    if type == dict:
        return undump(data)
    else:
        return type(data)

# Check if data already exists
def isDataExists(artist):
    return getData(artist, 1) == None


# Create
def createData(artist):
    if not isDataExists(artist):
        raise ce.SqlNoEntry(f"Data already found for '{artist}'.")

    crsr.execute(f"""
            INSERT INTO database
            VALUES ('{artist}', '{{}}', '{{}}', '0')
    """)
    cxn.commit()

# Edit
def editData(artist, **kwargs):
    if isDataExists(artist):
        raise ce.SqlNoEntry(f"Data already found for '{artist}'.")

    for key, value in kwargs.items():
        if isinstance(value, dict):
            value = redump(value)
        crsr.execute(f"""
            UPDATE database SET {key} = '{value}'
            WHERE guild_id = '{artist}'
        """)
    cxn.commit()


# Delete
def deleteData(artist):
    if not isDataExists(artist):
        raise ce.SqlNoEntry(f"Data being deleted doesn't exist for '{artist}'.")
    
    crsr.execute(f"""
        DELETE FROM database
        WHERE guildId = '{artist}'
    """)
    cxn.commit()
    


# createData("beans")
# insertData("beans", claim_channel_data="true")
# print(getData("beans", "claim_channel_data"))


# cxn.commit()
# cxn.close()