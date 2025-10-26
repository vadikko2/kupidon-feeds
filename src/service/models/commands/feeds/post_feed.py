import cqrs
import pydantic

from domain.entities import feed as feed_entity


class PostFeed(cqrs.Request):
    account_id: str
    text: str

    images: list[pydantic.UUID4]


class PostFeedResponse(cqrs.Response):
    feed: feed_entity.Feed
