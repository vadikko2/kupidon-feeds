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
            # Получаем количество подписчиков
            followers_count = await self.uow.followers_repository.count_followers(
                request.account_id,
            )
            # Получаем количество подписок
            following_count = await self.uow.followers_repository.count_following(
                request.account_id,
            )
            # Получаем количество feeds
            feeds_count = await self.uow.feeds_repository.count_feeds(
                request.account_id,
            )

            return get_account_info_model.GetAccountInfoResponse(
                account_id=request.account_id,
                followers_count=followers_count,
                following_count=following_count,
                feeds_count=feeds_count,
            )
