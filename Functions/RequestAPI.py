import json
import requests
import urllib

from GlobalVariables import variables as varss


def makeRequest(requestType, path, data={}, json={}, apiLink=varss.apiLink, apiHeaders=varss.apiHeaders):
    newUrl = f"{apiLink}{path}"

    if len(data) > 0:
        response = requests.request(requestType, newUrl, headers=apiHeaders, data=data)
    
    if len(json) > 0:
        response = requests.request(requestType, newUrl, headers=apiHeaders, json=json)

    response.raise_for_status()
    return response.json()
