import pydantic


class Follower(pydantic.BaseModel, frozen=True):
    follower: str
    follow_for: str

    followed_at: pydantic.NaiveDatetime
