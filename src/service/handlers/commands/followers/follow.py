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
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self) -> typing.List[event.Event]:
        return []

    async def handle(self, request: follow_model.Follow) -> follow_model.FollowResponse:
        # TODO тут необходимо сходить в сервис профилей и посмотреть существует ли пользователь,
        #  на которого мы пытаемся подписаться
        follower = follower_entity.Follower(
            follower=request.follower,
            follow_for=request.follow_for,
            followed_at=datetime.datetime.now(),
        )
        if follower is None:
            raise service_exceptions.UserNotFound(request.follow_for)
        async with self.uow:
            await self.uow.followers_repository.add(follower)
            await self.uow.commit()

        return follow_model.FollowResponse(follower=follower)
