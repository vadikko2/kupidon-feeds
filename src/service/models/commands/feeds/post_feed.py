import dataclasses
import uuid

import cqrs

from domain.entities import feed as feed_entity


@dataclasses.dataclass
class PostFeed(cqrs.DCRequest):
    account_id: str
    text: str
    images: list[uuid.UUID] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class PostFeedResponse(cqrs.DCResponse):
    feed: feed_entity.Feed
