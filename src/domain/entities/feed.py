import dataclasses
import datetime
import uuid

from domain.entities import images as images_entities


@dataclasses.dataclass(frozen=True)
class Feed:
    """
    Feed entity
    """

    feed_id: uuid.UUID
    account_id: str
    has_followed: bool

    text: str

    images: list[images_entities.Image] = dataclasses.field(default_factory=list)
    has_liked: bool = False
    created_at: datetime.datetime = dataclasses.field(
        default_factory=datetime.datetime.now,
    )
    updated_at: datetime.datetime | None = None

    likes_count: int = 0
    views_count: int = 0
