import typing

import cqrs
from cqrs.events import event

from service import exceptions
from service.interfaces import unit_of_work
from service.models.commands.feeds import delete_feed as delete_feed_model


class DeleteFeedHandler(cqrs.RequestHandler[delete_feed_model.DeleteFeed, None]):
    def __init__(
        self,
        uow_factory: unit_of_work.UoWFactory,
    ):
        self.uow = uow_factory()
        self._events = []

    @property
    def events(self) -> typing.List[event.Event]:
        return []

    async def handle(self, request: delete_feed_model.DeleteFeed) -> None:
        async with self.uow:
            feed = await self.uow.feeds_repository.get_by_id(request.feed_id)
            if feed is not None and feed.account_id != request.account_id:
                raise exceptions.UserDoesNotOwnFeed(
                    account_id=request.account_id,
                    feed_id=request.feed_id,
                )

            await self.uow.feeds_repository.delete(request.feed_id)
            await self.uow.commit()
