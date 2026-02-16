import dataclasses
import uuid

import cqrs

from domain.entities import feed


@dataclasses.dataclass
class GetAccountFeeds(cqrs.DCRequest):
    account_id: str
    limit: int
    offset: int
    current_account_id: str | None = None


@dataclasses.dataclass
class GetAccountFeedsResponse(cqrs.DCResponse):
    account_id: str
    feeds: list[feed.Feed] = dataclasses.field(default_factory=list)
    limit: int = 0
    offset: int = 0
    total_count: int = 0


@dataclasses.dataclass
class GetFeeds(cqrs.DCRequest):
    feed_ids: list[uuid.UUID]
    current_account_id: str | None = None


@dataclasses.dataclass
class GetFeedsResponse(cqrs.DCResponse):
    feeds: list[feed.Feed] = dataclasses.field(default_factory=list)
