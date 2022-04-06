"""Interacts with the VADB API."""


import json
import requests

import backend.logging.loggers as lgr
import backend.other.other_functions as o_f

from . import consts
from . import endpoints as endp


def clean_payload(payload: dict):
    """Cleans the payload."""
    new_payload = {}
    for key, value in payload.items():
        if isinstance(value, (list, dict)):
            new_payload[key] = json.dumps(value)
        else:
            new_payload[key] = value

    return new_payload


def make_request(
        endpoint: endp.Endpoint,
        payload: dict = None,
        to_dict = False,

        files: tuple[str, tuple[str, bytes, str]] = None,
        stream = False,
        ) -> None | requests.models.Response | dict:
    """Interacts with the VADB API."""
    if payload is None:
        payload = {}

    new_payload = clean_payload(payload)

    log_message_main = (
        f"{endpoint.request_type} -> {endpoint.link}: "
        f"payload = {o_f.pr_print(payload)}, files = {o_f.pr_print([x[0] for x in files]) if files is not None else None}"
    )

    log_message = f"Send {log_message_main}"
    lgr.log_vadb.info(log_message)


    response = requests.request(
        endpoint.request_type, endpoint.link,
        headers = consts.API_HEADERS,
        data = new_payload,
        files = files,
        stream = stream
    )

    response.raise_for_status()

    if to_dict:
        response = response.json()
        log_message = f"Received {o_f.pr_print(response)}"
    else:
        log_message = f"Received {response.json()}"

    lgr.log_vadb.info(log_message)

    return response
