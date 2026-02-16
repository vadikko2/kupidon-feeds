import dataclasses

import cqrs

from domain.entities import images


@dataclasses.dataclass
class UploadImage(cqrs.DCRequest):
    uploader: str
    image: bytes = dataclasses.field(default=b"", repr=False)
    filename: str | None = None


@dataclasses.dataclass
class UploadImageResponse(cqrs.DCResponse):
    image: images.Image
