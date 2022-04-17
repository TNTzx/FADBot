"""Contains code for image handling."""


import io

import requests as req
import PIL.Image as PIL

from .... import api
from .... import excepts
from ... import artist_struct


# DEBUG add check for if image has been deleted

def get_req_image(url: str):
    """Gets the `Response` object of the URL for images."""
    return req.get(url, stream = True)


class Image(artist_struct.ArtistStruct):
    """Defines an image for uploading to VADB."""
    name: str = "image.png"
    default_mime_type = "image/png"
    default_format = "PNG"
    max_image_size: tuple[int, int] = (2000, 2000)
    vadb_link_ext: str = None
    vadb_key: str = None
    default_url: str = None

    def __init__(self, original_url: str = None):
        if original_url is None:
            original_url = self.default_url

        self.original_url = original_url


    def get_req_image(self):
        """Gets the request image."""
        response = get_req_image(self.original_url)
        response.raise_for_status()

        return response


    def get_pil_image(self, default_if_not_found: bool = False):
        """Gets the PIL image. Use the default for this `Image` if it's not found."""
        try:
            image = self.get_req_image()
        except (req.exceptions.HTTPError, req.exceptions.MissingSchema) as exc:
            if not default_if_not_found:
                raise excepts.VADBImageNotFound(self.original_url) from exc

            image = get_req_image(self.default_url)

        pil_image = PIL.open(image.raw)

        if pil_image.width >= self.max_image_size[0] or pil_image.height >= self.max_image_size[1]:
            pil_image = pil_image.resize(self.max_image_size)

        return pil_image

    def get_data(self, default_if_not_found: bool = False):
        """Gets the data from the PIL image."""
        with io.BytesIO() as b_io:
            self.get_pil_image(default_if_not_found = default_if_not_found).save(b_io, format = self.default_format)
            b_io.seek(0)
            return b_io.getvalue()


    def firebase_to_json(self):
        return {
            "url": self.original_url
        }

    @classmethod
    def firebase_from_json(cls, json: dict | list):
        return cls(
            original_url = json.get("url")
        )


    @classmethod
    def from_artist(cls, artist_id: int):
        """Gets the avatar / banner of an artist."""
        return cls(f"{api.consts.API_IMAGE_LINK}/{cls.vadb_link_ext}/{artist_id}")


DEFAULT_IMAGE_URL = "https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg"

class Proof(Image):
    """Artist proof."""
    default_url = DEFAULT_IMAGE_URL

class Avatar(Image):
    """Artist avatar."""
    vadb_link_ext = vadb_key = "avatar"
    max_image_size = (200, 200)
    default_url = "https://cdn.discordapp.com/attachments/870831279673860157/965122450906046504/unknown.png"

class Banner(Image):
    """Artist banner."""
    vadb_link_ext = vadb_key = "banner"
    max_image_size = (1920, 1080)
    default_url = "https://cdn.discordapp.com/attachments/870831279673860157/965122636088746014/unknown.png"


class ImageInfo(artist_struct.ArtistStruct):
    """Stores the images of the artist."""
    def __init__(
            self,
            avatar: Avatar = Avatar(),
            banner: Banner = Banner()
            ):
        self.avatar = avatar
        self.banner = banner


    def _to_image_list(self) -> list[Image]:
        """Returns an image list."""
        return [self.avatar, self.banner]

    def to_payload(self) -> dict | tuple | list:
        """Returns payload for this `ImageInfo`."""
        return {
            image.vadb_key: (
                image.name,
                image.get_data(default_if_not_found = True),
                image.default_mime_type
            ) for image in self._to_image_list()
        }


    def firebase_to_json(self):
        return {
            "avatar": self.avatar.firebase_to_json(),
            "banner": self.banner.firebase_to_json()
        }

    @classmethod
    def firebase_from_json(cls, json: dict | list):
        return cls(
            avatar = Avatar.firebase_from_json(json.get("avatar")),
            banner = Banner.firebase_from_json(json.get("banner"))
        )
