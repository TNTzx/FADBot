import json
import requests
import urllib

from GlobalVariables import variables as varss


def makeRequest(requestType, path, data: dict ={}, apiLink=varss.apiLink, apiHeaders=varss.apiHeaders):
    newUrl = f"{apiLink}{path}"

    newData = {}
    for key, value in data.items():
        if isinstance(value, (list, dict)):
            newData[key] = json.dumps(value)
        else:
            newData[key] = value

    response = requests.request(requestType, newUrl, headers=apiHeaders, data=newData)

    response.raise_for_status()
    return response.json()
