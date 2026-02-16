import dataclasses
import datetime
import uuid


@dataclasses.dataclass(frozen=True)
class Like:
    feed_id: uuid.UUID
    account_id: str
    liked_at: datetime.datetime
