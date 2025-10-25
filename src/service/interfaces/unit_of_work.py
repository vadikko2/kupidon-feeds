import abc
import typing

from service.interfaces.repositories import feeds, images


class UoW(abc.ABC):
    feeds_repository: feeds.IFeedsRepository
    images_repository: images.IImageRepository

    @abc.abstractmethod
    async def __aenter__(self) -> typing.Self:
        raise NotImplementedError

    @abc.abstractmethod
    async def commit(self):
        pass

    @abc.abstractmethod
    async def rollback(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rollback()
