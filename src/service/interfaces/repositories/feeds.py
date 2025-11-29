import abc
import uuid

from domain.entities import feed as feed_entity


class IFeedsRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, feed: feed_entity.Feed) -> None:
        """
        Adds new feed into storage
        :raises service.exceptions.FeedAlreadyExists:
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, feed: feed_entity.Feed) -> None:
        """
        Updates feed in storage
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(self, feed_id: uuid.UUID) -> feed_entity.Feed | None:
        """
        Returns feed by id
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_ids(self, feed_ids: list[uuid.UUID]) -> list[feed_entity.Feed]:
        """
        Returns feeds by ids
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_account_feeds(
        self,
        account_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[feed_entity.Feed]:
        """
        Returns account feeds
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def count_feeds(self, account_id: str) -> int:
        """
        Returns account feeds count
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, feed_id: uuid.UUID) -> None:
        raise NotImplementedError
