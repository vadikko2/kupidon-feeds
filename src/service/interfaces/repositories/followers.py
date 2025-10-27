import abc

from domain.entities import follower as follower_entity


class IFollowersRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, follower: follower_entity.Follower) -> None:
        """
        Adds new follower
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, follower: str, follow_for: str) -> None:
        """
        Deletes follower
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def has_follow(self, follower: str, follow_for: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_followers(self, account_id: str) -> list[follower_entity.Follower]:
        """
        Returns followers
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_following(self, account_id: str) -> list[follower_entity.Follower]:
        """
        Returns following
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def count_followers(self, account_id: str) -> int:
        """
        Counts followers
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def count_following(self, account_id: str) -> int:
        """
        Counts following
        """
        raise NotImplementedError
