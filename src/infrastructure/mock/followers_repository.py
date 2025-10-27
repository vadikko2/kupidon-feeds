import orjson
from redis.asyncio import client

from domain.entities import follower as follower_entity
from service.interfaces.repositories import followers as followers_repository_interface


class RedisFollowersRepository(followers_repository_interface.IFollowersRepository):
    FOLLOWERS_KEY = "followers:{follower}:{follow_for}"

    FOLLOWERS_LIST_KEY = "followers_set:{account_id}"
    FOLLOWING_LIST_KEY = "following_set:{account_id}"

    def __init__(self, pipeline: client.Pipeline):
        self.pipeline = pipeline

    async def add(self, follower: follower_entity.Follower) -> None:
        follower_key = self.FOLLOWERS_KEY.format(
            follower=follower.follower,
            follow_for=follower.follow_for,
        )
        data = orjson.dumps(follower.model_dump())

        coroutine = await self.pipeline.set(follower_key, data)
        _ = (await coroutine.execute())[0]  # pyright: ignore[reportGeneralTypeIssues]

        follwers_list_key = self.FOLLOWERS_LIST_KEY.format(account_id=follower.follower)
        coroutine = await self.pipeline.sadd(  # pyright: ignore[reportGeneralTypeIssues]
            follwers_list_key,
            follower.follow_for,
        )
        _ = (await coroutine.execute())[0]  # pyright: ignore[reportAttributeAccessIssue]

        following_list_key = self.FOLLOWING_LIST_KEY.format(
            account_id=follower.follow_for,
        )
        coroutine = await self.pipeline.sadd(  # pyright: ignore[reportGeneralTypeIssues]
            following_list_key,
            follower.follower,
        )
        _ = (await coroutine.execute())[0]  # pyright: ignore[reportAttributeAccessIssue]

    async def delete(self, follower: str, follow_for: str) -> None:
        pass

    async def has_follow(self, follower: str, follow_for: str) -> bool:
        follwers_list_key = self.FOLLOWERS_LIST_KEY.format(account_id=follower)
        coroutine = await self.pipeline.sismember(  # pyright: ignore[reportGeneralTypeIssues]
            follwers_list_key,
            follow_for,
        )
        return (await coroutine.execute())[0]  # pyright: ignore[reportAttributeAccessIssue]

    async def get_followers(self, account_id: str) -> list[follower_entity.Follower]:
        return []

    async def get_following(self, account_id: str) -> list[follower_entity.Follower]:
        return []

    async def count_followers(self, account_id: str) -> int:
        return 0

    async def count_following(self, account_id: str) -> int:
        return 0
