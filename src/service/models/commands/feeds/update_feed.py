import cqrs
import pydantic

from domain.entities import feed as feed_entity


class UpdateFeed(cqrs.Request):
    account_id: str
    feed_id: pydantic.UUID4
    text: str

    images: list[pydantic.UUID4]


class UpdateFeedResponse(cqrs.Response):
    feed: feed_entity.Feed
