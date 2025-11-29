import pydantic


class Like(pydantic.BaseModel, frozen=True):
    feed_id: pydantic.UUID4 = pydantic.Field(description="Feed id")
    account_id: pydantic.StrictStr = pydantic.Field(description="Account id")
    liked_at: pydantic.NaiveDatetime = pydantic.Field(description="Liked at")
