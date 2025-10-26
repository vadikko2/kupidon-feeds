import cqrs
import pydantic

from domain.entities import images


class UploadImage(cqrs.Request):
    uploader: str
    image: bytes = pydantic.Field(exclude=True)
    filename: str | None


class UploadImageResponse(cqrs.Response):
    image: images.Image
