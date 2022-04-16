"""Contains the base class for queries."""


class BaseQuery():
    """Base class for queries."""
    def __init__(self, query_items: list = None):
        if len(query_items) == 0:
            self.query_items = None
        else:
            self.query_items = query_items


    @classmethod
    def from_search(cls, search_term: str):
        """Returns a `BaseQuery` for this search term."""
