import datetime
import typing

import cqrs
from cqrs.events import event

from domain.entities import feed as feed_entity
from service import exceptions
from service.interfaces import unit_of_work
from service.models.commands.feeds import update_feed as update_feed_model


class UpdateFeedHandler(
    cqrs.RequestHandler[
        update_feed_model.UpdateFeed,
        update_feed_model.UpdateFeedResponse,
    ],
):
    def __init__(
        self,
        uow: unit_of_work.UoW,
    ):
        self.uow = uow
        self._events = []

    @property
    def events(self) -> typing.List[event.Event]:
        return []

    async def handle(
        self,
        request: update_feed_model.UpdateFeed,
    ) -> update_feed_model.UpdateFeedResponse:
        async with self.uow:
            feed = await self.uow.feeds_repository.get_by_id(request.feed_id)
            if feed is None:
                raise exceptions.FeedNotFound(feed_id=request.feed_id)

            if feed.account_id != request.account_id:
                raise exceptions.UserDoesNotOwnFeed(
                    account_id=request.account_id,
                    feed_id=request.feed_id,
                )

            images = await self.uow.images_repository.get_many(*request.images)
            if len(images) != len(request.images):
                difference = set(request.images) - set([im.image_id for im in images])
                raise exceptions.ImageNotFound(image_id=difference.pop())

            already_bound_images = await self.uow.images_repository.get_many(
                *[im.image_id for im in feed.images],
            )

            images_for_unbinding = [
                im.unbound_from_feed()
                for im in already_bound_images
                if im not in images
            ]
            images_for_binding = [
                im.bound_to_feed(feed.feed_id)
                for im in images
                if im not in already_bound_images
            ]
            new_feed = feed_entity.Feed(
                feed_id=feed.feed_id,
                account_id=feed.account_id,
                has_followed=feed.has_followed,
                created_at=feed.created_at,
                updated_at=datetime.datetime.now(),
                text=request.text,
                images=images,
            )
            await self.uow.feeds_repository.update(new_feed)
            await self.uow.images_repository.update(
                *(images_for_binding + images_for_unbinding),
            )
            await self.uow.commit()

        return update_feed_model.UpdateFeedResponse(feed=new_feed)
