import pydantic


class PostFeed(pydantic.BaseModel):
    text: pydantic.StrictStr = pydantic.Field(
        description="Feed text",
        max_length=4096,
        default="",
    )
    images: list[pydantic.UUID4] = pydantic.Field(min_length=1)


class UpdateFeed(PostFeed):
    pass


class FollowAccount(pydantic.BaseModel):
    account_id: pydantic.StrictStr = pydantic.Field(description="Account id")


class ViewFeed(pydantic.BaseModel):
    feed_id: pydantic.UUID4 = pydantic.Field(description="Feed id")
