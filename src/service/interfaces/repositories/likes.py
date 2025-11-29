import abc
import typing
import uuid

from domain.entities import like as like_entity

TotalLikesCount: typing.TypeAlias = int
GetLikesResult: typing.TypeAlias = tuple[TotalLikesCount, list[like_entity.Like]]


class ILikesRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, like: like_entity.Like) -> None:
        """
        Add new like for feed
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, feed_id: uuid.UUID, account_id: str) -> None:
        """
        Delete feed like
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_feed_id(
        self,
        feed_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> GetLikesResult:
        """
        Returns feed likes
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def has_like(self, feed_id: uuid.UUID, account_id: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    async def count_by_feed_id(self, feed_id: uuid.UUID) -> TotalLikesCount:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_feed_id_and_account_id(
        self,
        feed_id: uuid.UUID,
        account_id: str,
    ) -> like_entity.Like | None:
        """
        Returns like by feed_id and account_id if exists
        """
        raise NotImplementedError
