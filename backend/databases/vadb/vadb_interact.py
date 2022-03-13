"""Interacts with the VADB API."""

import os
import json
import requests

import global_vars.loggers as lgr
import backend.other_functions as o_f

from . import file as apifile


# API
API_LINK = "https://fadb.live/api"
API_AUTH_TOKEN = os.environ["FadbAuthToken"]
API_HEADERS = {
    "Authorization": f"Basic {API_AUTH_TOKEN}",
    "Content-Type": "application/form-data"
}


def clean_payload(payload: dict):
    """Cleans the payload."""
    new_payload = {}
    for key, value in payload.items():
        if isinstance(value, (list, dict)):
            new_payload[key] = json.dumps(value)
        else:
            new_payload[key] = value

    return new_payload


def make_request(request_type, path, payload: dict = None, files: apifile.APIFileList = None):
    """Interacts with the VADB API."""
    if payload is None:
        payload = {}

    url = f"{API_LINK}{path}"
    new_payload = clean_payload(payload)

    if request_type != "GET":
        log_message_main = f"{request_type} -> {url}: payload = {o_f.pr_print(payload)}, files = "

        log_message = f"Send {log_message_main}"
        lgr.log_vadb.info(log_message)


    if files is not None:
        files = files.to_payload()


    response = requests.request(
        request_type, url, headers = API_HEADERS,
        data = new_payload,
        files = files
    )

    response.raise_for_status()
    final_response = response.json()

    log_message = f"Received {o_f.pr_print(final_response)}"
    lgr.log_vadb.info(log_message)

    return final_response
