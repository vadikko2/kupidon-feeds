import dataclasses
import uuid

import cqrs


@dataclasses.dataclass
class UnlikeFeed(cqrs.DCRequest):
    feed_id: uuid.UUID
    account_id: str
