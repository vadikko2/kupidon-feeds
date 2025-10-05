import abc

import pydantic


class Image(pydantic.BaseModel):
    image: bytes = pydantic.Field(exclude=True)
    filename: str


class ImagesStorage(abc.ABC):
    @abc.abstractmethod
    async def upload(self, *images: Image) -> list[str]:
        """Uploads images to storage and returns its URL"""
        raise NotImplementedError
