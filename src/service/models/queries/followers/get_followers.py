import cqrs

from domain.entities import follower


class GetFollowers(cqrs.Request):
    account_id: str
    limit: int
    offset: int


class GetFollowersResponse(cqrs.Response):
    account_id: str
    followers: list[follower.Follower]
    limit: int
    offset: int
    total_count: int
