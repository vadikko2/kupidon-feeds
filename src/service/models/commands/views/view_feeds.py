import dataclasses
import uuid

import cqrs


@dataclasses.dataclass
class ViewFeeds(cqrs.DCRequest):
    feed_ids: list[uuid.UUID]
    account_id: str


@dataclasses.dataclass
class ViewFeedsResponse(cqrs.DCResponse):
    pass
