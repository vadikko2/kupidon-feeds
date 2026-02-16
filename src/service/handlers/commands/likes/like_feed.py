import datetime
import typing

import cqrs
from cqrs.events import event

from domain.entities import like as like_entity
from service import exceptions
from service.interfaces import unit_of_work
from service.models.commands.likes import like_feed as like_feed_model


class LikeFeedHandler(
    cqrs.RequestHandler[like_feed_model.LikeFeed, like_feed_model.LikeFeedResponse],
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
        request: like_feed_model.LikeFeed,
    ) -> like_feed_model.LikeFeedResponse:
        async with self.uow:
            if not await self.uow.feeds_repository.exists(request.feed_id):
                raise exceptions.FeedNotFound(feed_id=request.feed_id)

            # Проверяем, есть ли уже лайк от этого пользователя (идемпотентность)
            existing_like = (
                await self.uow.likes_repository.get_by_feed_id_and_account_id(
                    request.feed_id,
                    request.account_id,
                )
            )

            if existing_like is not None:
                # Если лайк уже есть, просто возвращаем существующий лайк
                # Это делает метод идемпотентным
                return like_feed_model.LikeFeedResponse(like=existing_like)

            # Создаем новый лайк
            new_like = like_entity.Like(
                feed_id=request.feed_id,
                account_id=request.account_id,
                liked_at=datetime.datetime.now(),
            )

            await self.uow.likes_repository.add(new_like)
            await self.uow.commit()

        return like_feed_model.LikeFeedResponse(like=new_like)
