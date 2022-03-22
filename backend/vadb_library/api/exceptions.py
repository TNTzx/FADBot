"""Checks if a response is valid or invalid. Used for catching exceptions."""


import requests as req


def check_artist_already_exists(response: req.models.Response):
    """Checks if the response returned that the artist already exists."""
    return \
        response.status_code == 409 and \
        response.json()["message"] == "A artist already exists with that name."
