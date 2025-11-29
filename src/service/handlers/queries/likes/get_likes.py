import typing

import cqrs
from cqrs.events import event

from service import exceptions
from service.interfaces import unit_of_work
from service.models.queries.likes import get_likes as get_likes_model


class GetLikesHandler(
    cqrs.RequestHandler[get_likes_model.GetLikes, get_likes_model.GetLikesResponse],
):
    def __init__(
        self,
        uow_factory: unit_of_work.UoWFactory,
    ):
        self.uow = uow_factory()

    @property
    def events(self) -> typing.List[event.Event]:
        return []

    async def handle(
        self,
        request: get_likes_model.GetLikes,
    ) -> get_likes_model.GetLikesResponse:
        async with self.uow:
            # Проверяем, существует ли feed
            feed = await self.uow.feeds_repository.get_by_id(request.feed_id)
            if feed is None:
                raise exceptions.FeedNotFound(feed_id=request.feed_id)

            # Получаем лайки
            total_count, likes = await self.uow.likes_repository.get_by_feed_id(
                request.feed_id,
                limit=request.limit,
                offset=request.offset,
            )

            return get_likes_model.GetLikesResponse(
                feed_id=request.feed_id,
                likes=likes,
                limit=request.limit,
                offset=request.offset,
                total_count=total_count,
            )
