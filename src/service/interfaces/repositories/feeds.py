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
    async def exists(self, feed_id: uuid.UUID) -> bool:
        """
        Returns True if a feed with the given id exists (lightweight check).
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(
        self,
        feed_id: uuid.UUID,
        current_account_id: str | None = None,
    ) -> feed_entity.Feed | None:
        """
        Returns feed by id
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_ids(
        self,
        feed_ids: list[uuid.UUID],
        current_account_id: str | None = None,
    ) -> list[feed_entity.Feed]:
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
        current_account_id: str | None = None,
    ) -> tuple[list[feed_entity.Feed], int]:
        """
        Returns (account feeds, total count) in one query. Hot path.
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
        """
        Deletes feed by id. Idempotent: does not raise if the feed does not exist.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_account_info_counts(self, account_id: str) -> tuple[int, int, int]:
        """
        Returns (followers_count, following_count, feeds_count) in one query.
        """
        raise NotImplementedError
