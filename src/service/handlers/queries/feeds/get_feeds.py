import typing

import cqrs
from cqrs.events import event

from service.interfaces import unit_of_work
from service.models.queries.feeds import get_feeds


class GetAccountFeedsHandler(
    cqrs.RequestHandler[get_feeds.GetAccountFeeds, get_feeds.GetAccountFeedsResponse],
):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self) -> typing.List[event.Event]:
        return []

    async def handle(
        self,
        request: get_feeds.GetAccountFeeds,
    ) -> get_feeds.GetAccountFeedsResponse:
        async with self.uow:
            all_account_feeds = await self.uow.feeds_repository.get_account_feeds(
                request.account_id,
            )
            account_feeds_count = await self.uow.feeds_repository.count_feeds(
                request.account_id,
            )
            account_feeds = all_account_feeds[
                request.offset : request.offset + request.limit
            ]
            return get_feeds.GetAccountFeedsResponse(
                account_id=request.account_id,
                feeds=account_feeds,
                limit=request.limit,
                offset=request.offset,
                total_count=account_feeds_count,
            )
