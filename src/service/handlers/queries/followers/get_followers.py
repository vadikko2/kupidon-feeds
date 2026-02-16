import typing

import cqrs
from cqrs.events import event

from service.interfaces import unit_of_work
from service.models.queries.followers import get_followers as get_followers_model


class GetFollowersHandler(
    cqrs.RequestHandler[
        get_followers_model.GetFollowers,
        get_followers_model.GetFollowersResponse,
    ],
):
    def __init__(self, uow_factory: unit_of_work.UoWFactory):
        self.uow = uow_factory()

    @property
    def events(self) -> typing.List[event.Event]:
        return []

    async def handle(
        self,
        request: get_followers_model.GetFollowers,
    ) -> get_followers_model.GetFollowersResponse:
        async with self.uow:
            followers, total_count = await self.uow.followers_repository.get_followers(
                request.account_id,
                limit=request.limit,
                offset=request.offset,
            )
            return get_followers_model.GetFollowersResponse(
                account_id=request.account_id,
                followers=followers,
                limit=request.limit,
                offset=request.offset,
                total_count=total_count,
            )
