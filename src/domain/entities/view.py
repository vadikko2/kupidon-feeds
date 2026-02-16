import dataclasses
import datetime
import uuid


@dataclasses.dataclass(frozen=True)
class View:
    feed_id: uuid.UUID
    account_id: str
    viewed_at: datetime.datetime
