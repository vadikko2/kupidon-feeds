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

    async def get_by_id(self, feed_id: uuid.UUID) -> feed_entity.Feed | None:
        """
        Returns feed by id
        """
        raise NotImplementedError
