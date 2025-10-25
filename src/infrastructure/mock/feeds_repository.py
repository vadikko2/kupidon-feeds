import orjson
from redis.asyncio import client

from domain.entities import feed as feed_entity
from service import exceptions
from service.interfaces.repositories import feeds as feeds_repository
from infrastructure.mock import images_repository as redis_images_repository


class RedisFeedsRepository(feeds_repository.IFeedsRepository):
    KEY_PATTERN = "feed:{feed_id}"

    def __init__(
        self,
        pipeline: client.Pipeline,
        images_repository: redis_images_repository.RedisImagesRepository,
    ):
        self.pipeline = pipeline
        self.images_repository = images_repository

    async def add(self, feed: feed_entity.Feed) -> None:
        key = self.KEY_PATTERN.format(feed_id=feed.feed_id)
        existed_coroutine = await self.pipeline.get(key)
        existed = (await existed_coroutine.execute())[0]
        if existed:
            raise exceptions.FeedAlreadyExists(feed_id=feed.feed_id)

        coroutine = await self.pipeline.set(key, orjson.dumps(feed.model_dump()))
        _ = (await coroutine.execute())[0]

    async def update(self, feed: feed_entity.Feed) -> None:
        pass
