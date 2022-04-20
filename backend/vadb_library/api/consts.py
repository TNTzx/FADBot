"""Stores constants."""


import os


BASE_LINK = "https://fadb.live"
API_LINK = f"{BASE_LINK}/api"
API_IMAGE_LINK = "https://fadb.live/images"
API_AUTH_TOKEN = os.environ["FadbAuthToken"]
API_HEADERS = {
    "Authorization": f"Basic {API_AUTH_TOKEN}"
}
