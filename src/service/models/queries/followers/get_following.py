import dataclasses

import cqrs

from domain.entities import follower


@dataclasses.dataclass
class GetFollowing(cqrs.DCRequest):
    account_id: str
    limit: int
    offset: int


@dataclasses.dataclass
class GetFollowingResponse(cqrs.DCResponse):
    account_id: str
    following: list[follower.Follower] = dataclasses.field(default_factory=list)
    limit: int = 0
    offset: int = 0
    total_count: int = 0
