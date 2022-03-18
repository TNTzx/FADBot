"""Contains code for image handling."""


import os
import io

import urllib.parse as urlparse
import requests as req

import PIL.Image as PIL

from .... import api

from ... import artist_struct as a_s


class Image(a_s.ArtistStruct):
    """Defines an image for uploading to VADB."""
    def __init__(self, name: str, pil_image: PIL.Image, original_url: str = None):
        self.name = name

        with io.BytesIO() as data_bytes:
            pil_image.save(data_bytes, format = "PNG")
            self.data = data_bytes.getvalue()

        self.original_url = original_url

    def __repr__(self):
        return f"ImageData({self.name})"


    def get_pil_image(self):
        """Gets the PIL Image from data."""
        return PIL.open(io.BytesIO(self.data))


    vadb_link_ext: str = None
    vadb_key: str = None


    @classmethod
    def from_url(cls, url: str):
        """Gets an Image from a URL."""
        url_parse = urlparse.urlparse(url)
        name = os.path.basename(url_parse.path)
        response = req.get(url, stream = True)
        pil_image = PIL.open(response.raw)
        return cls(
            name = name,
            pil_image = pil_image,
            original_url = url
        )

    @classmethod
    def from_artist(cls, artist_id: int):
        """Gets the avatar / banner of an artist."""
        return cls.from_url(f"{api.consts.API_IMAGE_LINK}/{cls.vadb_link_ext}/{artist_id}")


class Proof(Image):
    """Artist proof."""

class Avatar(Image):
    """Artist avatar."""
    vadb_link_ext = vadb_key = "avatar"

class Banner(Image):
    """Artist banner."""
    vadb_link_ext = vadb_key = "banner"


DEFAULT_IMAGE_URL = "https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg"
DEFAULT_PROOF = Proof.from_url(DEFAULT_IMAGE_URL)
DEFAULT_AVATAR = Avatar.from_url(DEFAULT_IMAGE_URL)
DEFAULT_BANNER = Banner.from_url(DEFAULT_IMAGE_URL)


class ImageInfo(a_s.ArtistStruct):
    """Stores the images of the artist."""
    def __init__(
            self,
            avatar: Avatar | Image = DEFAULT_AVATAR,
            banner: Banner | Image = DEFAULT_BANNER
            ):
        self.avatar = avatar
        self.banner = banner

    def _to_image_list(self) -> list[Avatar | Banner]:
        """Returns an image list."""
        return [self.avatar, self.banner]

    def to_payload(self) -> dict | tuple | list:
        return {
            image.vadb_key: image.data for image in self._to_image_list()
        }