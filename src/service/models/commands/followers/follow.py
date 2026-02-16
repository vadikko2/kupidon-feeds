import dataclasses

import cqrs

from domain.entities import follower as follower_entity


@dataclasses.dataclass
class Follow(cqrs.DCRequest):
    follower: str
    follow_for: str


@dataclasses.dataclass
class FollowResponse(cqrs.DCResponse):
    follower: follower_entity.Follower
