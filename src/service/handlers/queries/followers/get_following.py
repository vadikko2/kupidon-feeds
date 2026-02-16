import typing

import cqrs
from cqrs.events import event

from service.interfaces import unit_of_work
from service.models.queries.followers import get_following as get_following_model


class GetFollowingHandler(
    cqrs.RequestHandler[
        get_following_model.GetFollowing,
        get_following_model.GetFollowingResponse,
    ],
):
    def __init__(self, uow_factory: unit_of_work.UoWFactory):
        self.uow = uow_factory()

    @property
    def events(self) -> typing.List[event.Event]:
        return []

    async def handle(
        self,
        request: get_following_model.GetFollowing,
    ) -> get_following_model.GetFollowingResponse:
        async with self.uow:
            following, total_count = await self.uow.followers_repository.get_following(
                request.account_id,
                limit=request.limit,
                offset=request.offset,
            )
            return get_following_model.GetFollowingResponse(
                account_id=request.account_id,
                following=following,
                limit=request.limit,
                offset=request.offset,
                total_count=total_count,
            )
