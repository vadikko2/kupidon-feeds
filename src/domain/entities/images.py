import datetime
import uuid

import pydantic


class Image(pydantic.BaseModel):
    """
    Image entity
    """

    image_id: pydantic.UUID4
    feed_id: pydantic.UUID4 | None = None
    uploader: str
    url: str
    blurhash: str | None = None
    uploaded_at: pydantic.NaiveDatetime = pydantic.Field(
        default_factory=datetime.datetime.now,
    )
    order: int = 0

    def bound_to_feed(self, feed_id: uuid.UUID):
        if self.feed_id is not None:
            raise ValueError("Image already bound to feed")

        self.feed_id = feed_id
