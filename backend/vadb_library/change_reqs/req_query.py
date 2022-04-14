"""Request query module."""


from .. import queries
from . import change_req
from . import req_exc


class RequestQuery(queries.BaseQuery):
    """Represents a query for requests."""
    @classmethod
    def from_search(cls, search_term: str):
        all_requests = []
        for change_req_type in change_req.ChangeRequest.get_all_req_types():
            try:
                all_reqs_in_change_req = change_req_type.firebase_get_all_requests()
            except req_exc.ChangeReqNotFound:
                continue

            for req in all_reqs_in_change_req:
                if req.artist.check_if_match_query(search_term):
                    all_requests.append(req)

        if len(all_requests) == 0:
            raise req_exc.ChangeReqNotFound(f"No change request found for search term \"{search_term}\".")

        return all_requests

