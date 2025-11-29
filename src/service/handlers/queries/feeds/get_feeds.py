import typing

import cqrs
from cqrs.events import event

from service.interfaces import unit_of_work
from service.models.queries.feeds import get_feeds


class GetAccountFeedsHandler(
    cqrs.RequestHandler[get_feeds.GetAccountFeeds, get_feeds.GetAccountFeedsResponse],
):
    def __init__(self, uow_factory: unit_of_work.UoWFactory):
        self.uow = uow_factory()

    @property
    def events(self) -> typing.List[event.Event]:
        return []

    async def handle(
        self,
        request: get_feeds.GetAccountFeeds,
    ) -> get_feeds.GetAccountFeedsResponse:
        async with self.uow:
            # Получаем feeds с пагинацией на уровне БД
            account_feeds = await self.uow.feeds_repository.get_account_feeds(
                request.account_id,
                limit=request.limit,
                offset=request.offset,
            )
            account_feeds_count = await self.uow.feeds_repository.count_feeds(
                request.account_id,
            )
            return get_feeds.GetAccountFeedsResponse(
                account_id=request.account_id,
                feeds=account_feeds,
                limit=request.limit,
                offset=request.offset,
                total_count=account_feeds_count,
            )


class GetFeedsHandler(
    cqrs.RequestHandler[get_feeds.GetFeeds, get_feeds.GetFeedsResponse],
):
    def __init__(self, uow_factory: unit_of_work.UoWFactory):
        self.uow = uow_factory()

    @property
    def events(self) -> typing.List[event.Event]:
        return []

    async def handle(
        self,
        request: get_feeds.GetFeeds,
    ) -> get_feeds.GetFeedsResponse:
        async with self.uow:
            feeds = await self.uow.feeds_repository.get_by_ids(request.feed_ids)
            return get_feeds.GetFeedsResponse(feeds=feeds)
