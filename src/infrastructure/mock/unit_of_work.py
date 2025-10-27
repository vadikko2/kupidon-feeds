import typing

import redis.asyncio as redis

from infrastructure.mock import (
    feeds_repository as redis_feeds_repository,
    images_repository as redis_images_repository,
    followers_repository as redis_followers_repository,
)
from service.interfaces import unit_of_work


class RedisUoW(unit_of_work.UoW):
    def __init__(self, redis_factory: typing.Callable[[], redis.Redis]):
        self._redis = redis_factory()

    async def __aenter__(self) -> typing.Self:
        self.pipeline = self._redis.pipeline()
        im_repository = redis_images_repository.RedisImagesRepository(self.pipeline)
        flw_repository = redis_followers_repository.RedisFollowersRepository(
            self.pipeline,
        )

        self.followers_repository = flw_repository
        self.images_repository = im_repository
        self.feeds_repository = redis_feeds_repository.RedisFeedsRepository(
            self.pipeline,
            im_repository,
        )

        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await super().__aexit__(exc_type, exc_value, traceback)
        del self.pipeline

    async def commit(self) -> None:
        await self.pipeline.execute()

    async def rollback(self) -> None:
        await self.pipeline.discard()
