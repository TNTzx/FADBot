"""Request query module."""


import nextcord as nx

from .. import queries
from . import change_req
from . import req_exc


class RequestQuery(queries.BaseQuery):
    """Represents a query for requests."""
    def __init__(self, query_items: list[change_req.ChangeRequest] = None):
        self.query_items = query_items


    def split_diff_req_types(self):
        """Splits this `RequestQuery` into other `RequestQuery`s. Returns a list of all `RequestQuery`s with only one type of `ChangeRequest`."""
        all_reqs = {
            change_req_type: []
            for change_req_type in change_req.ChangeRequest.get_all_req_types()
        }
        for request in self.query_items:
            all_reqs[type(request)].append(request)

        req_splits = [self.__class__(req) for req in all_reqs.values()]

        return [req_split for req_split in req_splits if len(req_split) != 0]


    @classmethod
    def from_search(cls, search_term: str):
        all_requests: list[change_req.ChangeRequest] = []
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

        return cls(all_requests)


    def generate_embed(
            self,
            title: str = None,
            description: str = None,
            footer: str = None
            ):
        embed = nx.Embed(
            color = 0xFF0000,
            title = title,
            description = description
        )

        change_req_splits = self.split_diff_req_types()

        emb_reqs = []

        for change_req_split in change_req_splits:
            emb_req_split = [
                f"\t**{change_req.artist.vadb_info.artist_id}**: {change_req.artist.name}"
                for change_req in change_req_split.query_items
            ]
            emb_req_split = '\n'.join(emb_req_split)

            emb_reqs.append((
                f"{change_req_split.query_items[0].type_.capitalize()} requests:\n"
                f"{emb_req_split}"
            ))

        embed.add_field(
            name = "_ _",
            value = "\n".join(emb_reqs)
        )

        if footer is not None:
            embed.set_footer(text = footer)

        return embed
