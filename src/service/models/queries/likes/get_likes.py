import cqrs
import pydantic

from domain.entities import like as like_entity


class GetLikes(cqrs.Request):
    feed_id: pydantic.UUID4
    limit: int
    offset: int


class GetLikesResponse(cqrs.Response):
    feed_id: pydantic.UUID4
    likes: list[like_entity.Like]
    limit: int
    offset: int
    total_count: int
