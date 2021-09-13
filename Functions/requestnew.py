import main
import requests
import urllib

async def makeRequest(type, path, payloadDict, apiLink=main.apiLink, apiHeaders=main.apiHeaders):
    newUrl = f"{apiLink}{path}"
    payloadStr = urllib.parse.urlencode(payloadDict)
    response = requests.request(type, newUrl, headers=apiHeaders, data=payloadStr)

    return response.json()