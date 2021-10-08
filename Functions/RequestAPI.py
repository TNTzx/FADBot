import json
import requests
import urllib

from GlobalVariables import variables as vars

def makeRequest(requestType, path, data={}, apiLink=vars.apiLink, apiHeaders=vars.apiHeaders):
    newUrl = f"{apiLink}{path}"
    payloadStr = urllib.parse.urlencode(data)
    response = requests.request(requestType, newUrl, headers=apiHeaders, data=payloadStr)

    response.raise_for_status()
    return response.json()