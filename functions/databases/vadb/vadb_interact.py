"""Interacts with the VADB API."""

import json
import requests

import global_vars.variables as vrs
import global_vars.loggers as lgr
import functions.other_functions as o_f


def make_request(request_type, path, data: dict = None):
    """Interacts with the VADB API."""
    if data is None:
        data = {}

    api_link = vrs.API_LINK
    api_headers = vrs.API_HEADERS

    url = f"{api_link}{path}"

    new_data = {}
    for key, value in data.items():
        if isinstance(value, (list, dict)):
            new_data[key] = json.dumps(value)
        else:
            new_data[key] = value

    if request_type != "GET":
        log_message_main = f"{request_type} -> {url}: {o_f.pr_print(data)}"

        log_message = f"Send {log_message_main}"
        lgr.log_vadb.info(log_message)

    response = requests.request(request_type, url, headers=api_headers, data=new_data)

    response.raise_for_status()
    final_response = response.json()

    log_message = f"Received {o_f.pr_print(final_response)}"
    lgr.log_vadb.info(log_message)

    return final_response
