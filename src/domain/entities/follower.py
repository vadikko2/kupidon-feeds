import dataclasses
import datetime


@dataclasses.dataclass(frozen=True)
class Follower:
    follower: str
    follow_for: str
    followed_at: datetime.datetime
