"""Interacts with the VADB API."""

import json
import requests

from global_vars import variables as vrs


def make_request(request_type, path, data: dict):
    """Interacts with the VADB API."""
    api_link=vrs.API_LINK
    api_headers=vrs.API_HEADERS

    url = f"{api_link}{path}"

    new_data = {}
    for key, value in data.items():
        if isinstance(value, (list, dict)):
            new_data[key] = json.dumps(value)
        else:
            new_data[key] = value

    response = requests.request(request_type, url, headers=api_headers, data=new_data)

    response.raise_for_status()
    return response.json()
