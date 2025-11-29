import typing

import cqrs
from cqrs.events import event

from service.interfaces import unit_of_work
from service.models.commands.followers import unfollow as unfollow_model


class UnfollowHandler(
    cqrs.RequestHandler[unfollow_model.Unfollow, None],
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
        request: unfollow_model.Unfollow,
    ) -> None:
        async with self.uow:
            # Проверяем, существует ли подписка
            has_follow = await self.uow.followers_repository.has_follow(
                follower=request.follower,
                follow_for=request.follow_for,
            )

            if not has_follow:
                # Если подписки нет, просто возвращаемся без ошибки (идемпотентность)
                return

            # Удаляем подписку
            await self.uow.followers_repository.delete(
                follower=request.follower,
                follow_for=request.follow_for,
            )
            await self.uow.commit()
