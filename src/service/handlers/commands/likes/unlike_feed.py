import typing

import cqrs
from cqrs.events import event

from service import exceptions
from service.interfaces import unit_of_work
from service.models.commands.likes import unlike_feed as unlike_feed_model


class UnlikeFeedHandler(
    cqrs.RequestHandler[unlike_feed_model.UnlikeFeed, None],
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
        request: unlike_feed_model.UnlikeFeed,
    ) -> None:
        async with self.uow:
            # Проверяем, существует ли feed
            feed = await self.uow.feeds_repository.get_by_id(request.feed_id)
            if feed is None:
                raise exceptions.FeedNotFound(feed_id=request.feed_id)

            # Проверяем, есть ли лайк от этого пользователя
            has_like = await self.uow.likes_repository.has_like(
                request.feed_id,
                request.account_id,
            )

            if not has_like:
                # Если лайка нет, просто возвращаемся без ошибки (идемпотентность)
                return

            # Удаляем лайк
            await self.uow.likes_repository.delete(request.feed_id, request.account_id)
            await self.uow.commit()
