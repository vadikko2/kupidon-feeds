import dataclasses
import uuid

import cqrs


@dataclasses.dataclass
class DeleteFeed(cqrs.DCRequest):
    account_id: str
    feed_id: uuid.UUID
