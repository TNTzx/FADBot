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
    def __init__(self, original_url: str = None):
        self.original_url = original_url

    def __repr__(self):
        return f"ImageData({self.get_pil_image()})"


    name: str = "image.png"
    default_mime_type = "image/png"
    default_format = "PNG"
    max_image_size: tuple[int, int] = (2000, 2000)


    def get_pil_image(self):
        """Gets the PIL image."""
        response = req.get(self.original_url, stream = True)
        pil_image = PIL.open(response.raw)

        if pil_image.width >= self.max_image_size[0] or pil_image.height >= self.max_image_size[1]:
            pil_image = pil_image.resize(self.max_image_size)

        return pil_image


    def get_data(self):
        """Gets the data from the PIL image."""
        with io.BytesIO() as b_io:
            self.get_pil_image().save(b_io, format = self.default_format)
            b_io.seek(0)
            return b_io.getvalue()


    vadb_link_ext: str = None
    vadb_key: str = None


    @classmethod
    def from_artist(cls, artist_id: int):
        """Gets the avatar / banner of an artist."""
        return cls(f"{api.consts.API_IMAGE_LINK}/{cls.vadb_link_ext}/{artist_id}")


class Proof(Image):
    """Artist proof."""

class Avatar(Image):
    """Artist avatar."""
    vadb_link_ext = vadb_key = "avatar"
    max_image_size = (200, 200)

class Banner(Image):
    """Artist banner."""
    vadb_link_ext = vadb_key = "banner"
    max_image_size = (1920, 1080)


DEFAULT_IMAGE_URL = "https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg"
DEFAULT_PROOF = Proof(DEFAULT_IMAGE_URL)
DEFAULT_AVATAR = Avatar(DEFAULT_IMAGE_URL)
DEFAULT_BANNER = Banner(DEFAULT_IMAGE_URL)


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
            image.vadb_key: (
                image.name,
                image.get_data(),
                image.default_mime_type
            ) for image in self._to_image_list()
        }
