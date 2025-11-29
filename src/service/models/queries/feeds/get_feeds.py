import uuid

import cqrs

from domain.entities import feed


class GetAccountFeeds(cqrs.Request):
    account_id: str

    limit: int
    offset: int


class GetAccountFeedsResponse(cqrs.Response):
    account_id: str
    feeds: list[feed.Feed]
    limit: int
    offset: int

    total_count: int


class GetFeeds(cqrs.Request):
    feed_ids: list[uuid.UUID]


class GetFeedsResponse(cqrs.Response):
    feeds: list[feed.Feed]
