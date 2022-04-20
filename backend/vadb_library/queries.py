"""Contains the base class for queries."""


class BaseQuery():
    """Base class for queries."""
    def __init__(self, query_items = None):
        self.query_items = query_items


    @classmethod
    def from_search(cls, search_term: str):
        """Returns a `BaseQuery` for this search term."""


    def generate_embed(self, title: str, description: str, footer: str):
        """Generates an embed for this BaseQuery."""
