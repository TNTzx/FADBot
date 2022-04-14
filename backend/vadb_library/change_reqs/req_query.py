"""Request query module."""


from .. import queries
from . import change_req


class RequestQuery(queries.BaseQuery):
    """Represents a query for requests."""
    @classmethod
    def from_search(cls, search_term: str):
        for change_req_type in change_req.ChangeRequest.get_all_req_types():
            for c_req
