import requests
import urllib

from GlobalVariables import variables as vars

async def makeRequest(type, path, payloadDict, apiLink=vars.apiLink, apiHeaders=vars.apiHeaders):
    newUrl = f"{apiLink}{path}"
    payloadStr = urllib.parse.urlencode(payloadDict)
    response = requests.request(type, newUrl, headers=apiHeaders, data=payloadStr)

    return response.json()