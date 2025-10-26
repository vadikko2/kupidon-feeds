import uuid

import orjson
from redis.asyncio import client

from domain.entities import feed as feed_entity
from infrastructure.mock import images_repository as redis_images_repository
from service import exceptions
from service.interfaces.repositories import feeds as feeds_repository


class RedisFeedsRepository(feeds_repository.IFeedsRepository):
    FEED_KEY_PATTERN = "feed:{feed_id}"
    ACCOUNT_FEEDS_KEY_PATTERN = "account_feeds:{account_id}"

    def __init__(
        self,
        pipeline: client.Pipeline,
        images_repository: redis_images_repository.RedisImagesRepository,
    ):
        self.pipeline = pipeline
        self.images_repository = images_repository

    async def add(self, feed: feed_entity.Feed) -> None:
        key = self.FEED_KEY_PATTERN.format(feed_id=feed.feed_id)
        existed_coroutine = await self.pipeline.get(key)
        existed = (await existed_coroutine.execute())[0]
        if existed:
            raise exceptions.FeedAlreadyExists(feed_id=feed.feed_id)

        coroutine = await self.pipeline.set(key, orjson.dumps(feed.model_dump()))
        _ = (await coroutine.execute())[0]

        coroutine = await self.pipeline.sadd(  # pyright: ignore[reportGeneralTypeIssues]
            self.ACCOUNT_FEEDS_KEY_PATTERN.format(account_id=feed.account_id),
            str(feed.feed_id),
        )
        _ = (await coroutine.execute())[0]  # pyright: ignore[reportAttributeAccessIssue]

    async def update(self, feed: feed_entity.Feed) -> None:
        pass

    async def get_by_id(self, feed_id: uuid.UUID) -> feed_entity.Feed | None:
        pass

    async def get_account_feeds(self, account_id: str) -> list[feed_entity.Feed]:
        account_feeds_key = self.ACCOUNT_FEEDS_KEY_PATTERN.format(account_id=account_id)
        account_feed_ids_coroutine = await self.pipeline.smembers(  # pyright: ignore[reportGeneralTypeIssues]
            account_feeds_key,
        )
        account_feed_ids = (await account_feed_ids_coroutine.execute())[0]  # pyright: ignore[reportAttributeAccessIssue]
        if not account_feed_ids:
            return []

        feeds = []
        for feed_id in account_feed_ids:
            feed_key = self.FEED_KEY_PATTERN.format(feed_id=feed_id.decode())
            feed_coroutine = await self.pipeline.get(feed_key)
            feed_bytes = (await feed_coroutine.execute())[0]
            if not feed_bytes:
                continue
            feed = feed_entity.Feed.model_validate(orjson.loads(feed_bytes))
            feeds.append(feed)

        return feeds

    async def count_feeds(self, account_id: str) -> int:
        account_feeds_key = self.ACCOUNT_FEEDS_KEY_PATTERN.format(account_id=account_id)
        feed_ids_coroutine = await self.pipeline.scard(account_feeds_key)  # pyright: ignore[reportGeneralTypeIssues]
        feed_ids = (await feed_ids_coroutine.execute())[0]  # pyright: ignore[reportAttributeAccessIssue]
        return feed_ids
