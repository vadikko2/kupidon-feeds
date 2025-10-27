import cqrs

from domain.entities import follower as follower_entity


class Follow(cqrs.Request):
    follower: str
    follow_for: str


class FollowResponse(cqrs.Response):
    follower: follower_entity.Follower
