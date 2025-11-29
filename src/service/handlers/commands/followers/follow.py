import datetime
import typing

import cqrs
from cqrs.events import event

from domain.entities import follower as follower_entity
from service import exceptions as service_exceptions
from service.interfaces import unit_of_work
from service.models.commands.followers import follow as follow_model


class FollowHandler(
    cqrs.RequestHandler[follow_model.Follow, follow_model.FollowResponse],
):
    def __init__(self, uow_factory: unit_of_work.UoWFactory):
        self.uow = uow_factory()

    @property
    def events(self) -> typing.List[event.Event]:
        return []

    async def handle(self, request: follow_model.Follow) -> follow_model.FollowResponse:
        # TODO тут необходимо сходить в сервис профилей и посмотреть существует ли пользователь,
        #  на которого мы пытаемся подписаться

        # Проверка на попытку подписаться на самого себя
        if request.follower == request.follow_for:
            raise service_exceptions.CannotFollowSelf(request.follower)

        async with self.uow:
            # Проверяем, есть ли уже подписка (идемпотентность)
            existing_follower = await self.uow.followers_repository.get_follow(
                follower=request.follower,
                follow_for=request.follow_for,
            )

            if existing_follower is not None:
                # Если подписка уже есть, просто возвращаем существующую подписку
                # Это делает метод идемпотентным
                return follow_model.FollowResponse(follower=existing_follower)

            # Создаем новую подписку
            follower = follower_entity.Follower(
                follower=request.follower,
                follow_for=request.follow_for,
                followed_at=datetime.datetime.now(),
            )
            await self.uow.followers_repository.add(follower)
            await self.uow.commit()

        return follow_model.FollowResponse(follower=follower)
