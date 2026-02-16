import dataclasses
import uuid

import cqrs

from domain.entities import like as like_entity


@dataclasses.dataclass
class LikeFeed(cqrs.DCRequest):
    feed_id: uuid.UUID
    account_id: str


@dataclasses.dataclass
class LikeFeedResponse(cqrs.DCResponse):
    like: like_entity.Like
