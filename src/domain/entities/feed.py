import datetime

import pydantic

from domain.entities import images


class Feed(pydantic.BaseModel, frozen=True):
    """
    Feed entity
    """

    feed_id: pydantic.UUID4
    account_id: str
    has_followed: bool
    has_liked: bool = False

    created_at: pydantic.NaiveDatetime = pydantic.Field(
        default_factory=datetime.datetime.now,
    )
    updated_at: pydantic.NaiveDatetime | None = None

    text: str
    images: list[images.Image]

    likes_count: int = 0
    views_count: int = 0
