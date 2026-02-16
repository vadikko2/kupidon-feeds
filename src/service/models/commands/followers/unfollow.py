import dataclasses

import cqrs


@dataclasses.dataclass
class Unfollow(cqrs.DCRequest):
    follower: str
    follow_for: str
