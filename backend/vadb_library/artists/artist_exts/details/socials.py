"""Social links."""


import tldextract as tld

from ... import artist_struct


class Social(artist_struct.ArtistStruct):
    """Defines a social."""
    def __init__(
                self,
                link: str = "https://fadb.live"
            ):
        self.link = link

    def get_domain(self) -> str:
        """Gets the domain of the social link."""
        return tld.extract(self.link).domain


    def vadb_to_edit_json(self) -> dict | list:
        return {
            "link": self.link,
            "type": self.get_domain()
        }


    def firebase_to_json(self):
        return {
            "link": self.link
        }

    @classmethod
    def firebase_from_json(cls, json: dict | list | ...):
        return cls(
            link = json.get("link")
        )


class Socials(artist_struct.ArtistStruct):
    """Defines a social list."""
    def __init__(
                self,
                socials: list[Social] | None = None
            ):
        self.socials = socials


    def vadb_to_edit_json(self) -> dict | list:
        if self.socials is None:
            return None

        return [social.vadb_to_edit_json() for social in self.socials]


    def firebase_to_json(self):
        if self.socials is None:
            return None

        return [social.firebase_to_json() for social in self.socials]

    @classmethod
    def firebase_from_json(cls, json: dict | list | ...):
        return cls(
            socials = [
                Socials.firebase_from_json(social_json) for social_json in json
            ]
        )
