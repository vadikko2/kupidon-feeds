import abc
import typing

from service.interfaces.repositories import feeds, followers, images, likes, views


class UoW(abc.ABC):
    feeds_repository: feeds.IFeedsRepository
    images_repository: images.IImageRepository
    followers_repository: followers.IFollowersRepository
    likes_repository: likes.ILikesRepository
    views_repository: views.IViewsRepository

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


class UoWFactory(abc.ABC):
    @abc.abstractmethod
    def __call__(self) -> UoW:
        raise NotImplementedError
