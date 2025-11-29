import cqrs


class Unfollow(cqrs.Request):
    follower: str
    follow_for: str
