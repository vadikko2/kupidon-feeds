import pydantic


class Image(pydantic.BaseModel):
    id: pydantic.UUID4 = pydantic.Field(description="Image id")
    url: pydantic.StrictStr = pydantic.Field(description="Download image url")
    blurhash: pydantic.StrictStr = pydantic.Field(description="Blurhash")


class OrderedImage(pydantic.BaseModel):
    image: Image = pydantic.Field(description="Image")
    order: pydantic.NonNegativeInt = pydantic.Field(
        description="Image order",
        default=0,
    )


class Feed(pydantic.BaseModel):
    uuid: pydantic.UUID4 = pydantic.Field(description="Feed id")

    account_id: pydantic.StrictStr = pydantic.Field(description="Account id")

    created_at: pydantic.NaiveDatetime = pydantic.Field(description="Created at")
    updated_at: pydantic.NaiveDatetime | None = pydantic.Field(description="Updated at")

    text: pydantic.StrictStr = pydantic.Field(description="Feed text")
    images: list[OrderedImage] = pydantic.Field(description="Feed images", min_length=1)

    likes_count: pydantic.NonNegativeInt = pydantic.Field(
        description="Likes count",
        default=0,
    )
    views_count: pydantic.NonNegativeInt = pydantic.Field(
        description="Views count",
        default=0,
    )


class Feeds(pydantic.BaseModel):
    items: list[Feed] = pydantic.Field(description="Feeds", default_factory=list)

    @pydantic.computed_field()
    @property
    def total_count(self) -> pydantic.NonNegativeInt:
        return len(self.items)


class Like(pydantic.BaseModel):
    feed_id: pydantic.UUID4 = pydantic.Field(description="Feed id")
    account_id: pydantic.StrictStr = pydantic.Field(description="Account id")
    liked_at: pydantic.NaiveDatetime = pydantic.Field(description="Liked at")


class Follower(pydantic.BaseModel):
    follower: pydantic.StrictStr = pydantic.Field(description="Account id")
    follow_for: pydantic.StrictStr = pydantic.Field(description="Follow for")

    followed_at: pydantic.NaiveDatetime = pydantic.Field(description="Followed at")
