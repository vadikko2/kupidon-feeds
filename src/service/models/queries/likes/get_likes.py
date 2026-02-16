import dataclasses
import uuid

import cqrs

from domain.entities import like as like_entity


@dataclasses.dataclass
class GetLikes(cqrs.DCRequest):
    feed_id: uuid.UUID
    limit: int
    offset: int


@dataclasses.dataclass
class GetLikesResponse(cqrs.DCResponse):
    feed_id: uuid.UUID
    likes: list[like_entity.Like] = dataclasses.field(default_factory=list)
    limit: int = 0
    offset: int = 0
    total_count: int = 0
