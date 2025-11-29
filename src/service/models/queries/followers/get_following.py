import cqrs

from domain.entities import follower


class GetFollowing(cqrs.Request):
    account_id: str
    limit: int
    offset: int


class GetFollowingResponse(cqrs.Response):
    account_id: str
    following: list[follower.Follower]
    limit: int
    offset: int
    total_count: int
