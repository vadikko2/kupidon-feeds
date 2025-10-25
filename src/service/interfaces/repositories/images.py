import abc
import uuid

from domain.entities import images


class IImageRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, image: images.Image) -> None:
        """
        Saves new image info into storage
        :raises service.exceptions.ImageAlreadyExists:
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(self, image_id: uuid.UUID) -> images.Image | None:
        """
        Returns image info by id from storage
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_many(self, *image_id: uuid.UUID) -> list[images.Image]:
        """
        Returns many images by id
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, *image: images.Image):
        """
        Updates images by id
        :raises service.exceptions.ImageNotFound:
        """
        raise NotImplementedError
