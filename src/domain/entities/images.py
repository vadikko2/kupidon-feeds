import dataclasses
import datetime
import uuid


@dataclasses.dataclass(frozen=True)
class Image:
    """
    Image entity
    """

    image_id: uuid.UUID
    uploader: str
    url: str
    feed_id: uuid.UUID | None = None
    blurhash: str | None = None
    uploaded_at: datetime.datetime = dataclasses.field(
        default_factory=datetime.datetime.now,
    )
    order: int = 0

    def bound_to_feed(self, feed_id: uuid.UUID) -> "Image":
        if self.feed_id is not None:
            raise ValueError("Image already bound to feed")

        return Image(
            image_id=self.image_id,
            feed_id=feed_id,
            uploader=self.uploader,
            url=self.url,
            blurhash=self.blurhash,
            uploaded_at=self.uploaded_at,
            order=self.order,
        )

    def unbound_from_feed(self) -> "Image":
        if self.feed_id is None:
            raise ValueError("Image not bound to feed")

        return Image(
            image_id=self.image_id,
            feed_id=None,
            uploader=self.uploader,
            url=self.url,
            blurhash=self.blurhash,
            uploaded_at=self.uploaded_at,
            order=self.order,
        )
