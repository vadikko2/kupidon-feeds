import abc
import dataclasses


@dataclasses.dataclass
class Image:
    image: bytes = dataclasses.field(default=b"", repr=False)
    filename: str = dataclasses.field(default="")


class ImagesStorage(abc.ABC):
    @abc.abstractmethod
    async def upload(self, *images: Image) -> list[str]:
        """Uploads images to storage and returns its URL"""
        raise NotImplementedError
