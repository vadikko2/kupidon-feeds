import typing
import uuid

import cqrs
from cqrs.events import event

from domain.entities import feed as feed_entities
from service import exceptions
from service.interfaces import unit_of_work
from service.interfaces.storages import images_storage as images_storage_interface
from service.models.commands import post_feed


class PostFeedHandler(
    cqrs.RequestHandler[post_feed.PostFeed, post_feed.PostFeedResponse],
):
    def __init__(
        self,
        image_storage: images_storage_interface.ImagesStorage,
        uow: unit_of_work.UoW,
    ):
        self.image_storage = image_storage
        self.uow = uow
        self._events = []

    @property
    def events(self) -> typing.List[event.Event]:
        return self._events

    async def handle(self, request: post_feed.PostFeed) -> post_feed.PostFeedResponse:
        new_feed_id = uuid.uuid4()
        async with self.uow:
            images = await self.uow.images_repository.get_many(*request.images)

            if len(images) != len(request.images):
                difference = set(request.images) - set([im.image_id for im in images])
                raise exceptions.ImageNotFound(image_id=difference.pop())

            for image in images:
                if image.uploader != request.account_id:
                    raise exceptions.ImageNotFound(image_id=image.image_id)
                if image.feed_id is not None:
                    raise exceptions.ImageAlreadyBoundToFeed(
                        image_id=image.image_id,
                        feed_id=image.feed_id,
                    )
                image.bound_to_feed(new_feed_id)

            new_post = feed_entities.Feed(
                feed_id=uuid.uuid4(),
                account_id=request.account_id,
                has_followed=False,
                text=request.text,
                images=images,
            )
            await self.uow.feeds_repository.add(new_post)
            await self.uow.images_repository.update(*images)
            await self.uow.commit()

        return post_feed.PostFeedResponse(feed=new_post)
