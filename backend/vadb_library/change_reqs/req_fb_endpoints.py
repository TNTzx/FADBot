"""Requests's Firebase endpoints."""


import backend.firebase as firebase


class CurrentID(firebase.FBEndpointEnd):
    """Contains the current ID of the requests."""
    def __init__(self):
        super().__init__(name = "current_req_id", parent = firebase.ShortEndpoint.artist_change_reqs)

CURRENT_ID = CurrentID()
