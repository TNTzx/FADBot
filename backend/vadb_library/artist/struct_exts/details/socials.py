"""Social links."""


import tldextract as tld

from ... import artist_struct as a_s


class Social(a_s.ArtistStruct):
    """Defines a social."""
    def __init__(
                self,
                link: str = "https://fadb.live"
            ):
        self.link = link

    def get_domain(self) -> str:
        """Gets the domain of the social link."""
        return tld.extract(self.link).domain


class Socials(a_s.ArtistStruct):
    """Defines a social list."""
    def __init__(
                self,
                socials: list[Social] | None = None
            ):
        self.socials = socials
