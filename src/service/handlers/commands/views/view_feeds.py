import datetime
import typing

import cqrs
from cqrs.events import event

from domain.entities import view as view_entity
from service.interfaces import unit_of_work
from service.models.commands.views import view_feeds as view_feeds_model


class ViewFeedsHandler(
    cqrs.RequestHandler[view_feeds_model.ViewFeeds, view_feeds_model.ViewFeedsResponse],
):
    def __init__(
        self,
        uow_factory: unit_of_work.UoWFactory,
    ):
        self.uow = uow_factory()
        self._events = []

    @property
    def events(self) -> typing.List[event.Event]:
        return self._events

    async def handle(
        self,
        request: view_feeds_model.ViewFeeds,
    ) -> view_feeds_model.ViewFeedsResponse:
        async with self.uow:
            # Create view entities for all feed_ids
            views = [
                view_entity.View(
                    feed_id=feed_id,
                    account_id=request.account_id,
                    viewed_at=datetime.datetime.now(),
                )
                for feed_id in request.feed_ids
            ]

            # Batch add views with idempotency (ON CONFLICT DO NOTHING)
            await self.uow.views_repository.batch_add(views)
            await self.uow.commit()

        return view_feeds_model.ViewFeedsResponse()
