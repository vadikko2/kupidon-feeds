import typing

import cqrs
from cqrs.events import event

from service.interfaces import unit_of_work
from service.models.queries.followers import get_account_info as get_account_info_model


class GetAccountInfoHandler(
    cqrs.RequestHandler[
        get_account_info_model.GetAccountInfo,
        get_account_info_model.GetAccountInfoResponse,
    ],
):
    def __init__(self, uow_factory: unit_of_work.UoWFactory):
        self.uow = uow_factory()

    @property
    def events(self) -> typing.List[event.Event]:
        return []

    async def handle(
        self,
        request: get_account_info_model.GetAccountInfo,
    ) -> get_account_info_model.GetAccountInfoResponse:
        async with self.uow:
            (
                followers_count,
                following_count,
                feeds_count,
            ) = await self.uow.feeds_repository.get_account_info_counts(
                request.account_id,
            )
            return get_account_info_model.GetAccountInfoResponse(
                account_id=request.account_id,
                followers_count=followers_count,
                following_count=following_count,
                feeds_count=feeds_count,
            )
