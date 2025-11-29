import cqrs
import pydantic

from domain.entities import like as like_entity


class LikeFeed(cqrs.Request):
    feed_id: pydantic.UUID4
    account_id: str


class LikeFeedResponse(cqrs.Response):
    like: like_entity.Like
