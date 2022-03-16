"""Contains code for image handling."""


import os
import io

import typing as typ
import urllib.parse as urlparse
import requests as req

import PIL.Image as PIL

import backend.databases.vadb.vadb_interact as v_i
import backend.utils.new_dataclass as dt

from ... import artist_struct as a_s


class Image(a_s.ArtistStruct):
    """Defines an image for uploading to VADB."""
    def __init__(self, name: str, data: PIL.Image | bytes):
        self.name = name

        self.pil_image = data

        if isinstance(data, PIL.Image):
            with io.BytesIO() as data_bytes:
                data.save(data_bytes, format = "PNG")
                self.data = data_bytes.getvalue()
        else:
            self.data = data

    def __repr__(self):
        return f"ImageData({self.name})"


    vadb_link_ext: str = None
    vadb_key: str = None

    def to_payload(self) -> dict:
        return (
            self.vadb_key,
            (self.name, self.data, "image/png")
        )


    @classmethod
    def from_url(cls, url: str):
        """Gets an Image from a URL."""
        url_parse = urlparse.urlparse(url)
        name = os.path.basename(url_parse.path)
        response = req.get(url, stream = True)
        data = PIL.open(response.raw)
        return cls(
            name = name,
            data = data
        )

    @classmethod
    def from_artist(cls, artist_id: int):
        """Gets the avatar / banner of an artist."""
        return cls.from_url(f"{v_i.API_IMAGE_LINK}/{cls.vadb_link_ext}/{artist_id}")


class Proof(Image):
    """Artist proof."""

class Avatar(Image):
    """Artist avatar."""
    vadb_link_ext = vadb_key = "avatar"

class Banner(Image):
    """Artist banner."""
    vadb_link_ext = vadb_key = "banner"


DEFAULT_URL = "https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg"
DEFAULT_PROOF = Proof.from_url(DEFAULT_URL)
DEFAULT_AVATAR = Avatar.from_url(DEFAULT_URL)
DEFAULT_BANNER = Banner.from_url(DEFAULT_URL)


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
        return [image.to_payload() for image in self._to_image_list()]
