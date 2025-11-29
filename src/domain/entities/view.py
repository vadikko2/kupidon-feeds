import pydantic


class View(pydantic.BaseModel, frozen=True):
    feed_id: pydantic.UUID4 = pydantic.Field(description="Feed id")
    account_id: pydantic.StrictStr = pydantic.Field(description="Account id")
    viewed_at: pydantic.NaiveDatetime = pydantic.Field(description="Viewed at")
