import dataclasses
import uuid

import cqrs

from domain.entities import feed as feed_entity


@dataclasses.dataclass
class UpdateFeed(cqrs.DCRequest):
    account_id: str
    feed_id: uuid.UUID
    text: str
    images: list[uuid.UUID] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class UpdateFeedResponse(cqrs.DCResponse):
    feed: feed_entity.Feed
