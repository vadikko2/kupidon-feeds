import random

import cqrs
import fastapi
import pydantic
from fastapi_app import response
from fastapi_app.exception_handlers import registry

from presentation import dependencies
from presentation.api import security
from presentation.api.schemas import (
    pagination,
    requests as requests_schema,
    responses as responses_schema,
)
from service import exceptions as service_exceptions
from service.models.commands.followers import follow as follow_model
from service.models.queries.feeds import get_feeds as get_feeds_model

router = fastapi.APIRouter(prefix="/followers")


@router.post(
    "",
    status_code=fastapi.status.HTTP_201_CREATED,
    description="Follow for account",
    responses=registry.get_exception_responses(
        service_exceptions.GetUserIdError,
        service_exceptions.UnauthorizedError,
        service_exceptions.UserNotFound,
    ),
)
async def follow(
    body: requests_schema.FollowAccount = fastapi.Body(...),
    account_id: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> response.Response[responses_schema.Follower]:
    result: follow_model.FollowResponse = await mediator.send(
        follow_model.Follow(
            follower=account_id,
            follow_for=body.account_id,
        ),
    )
    return response.Response(
        result=responses_schema.Follower(
            follower=account_id,
            follow_for=body.account_id,
            followed_at=result.follower.followed_at,
        ),
    )


@router.get(
    "",
    status_code=fastapi.status.HTTP_200_OK,
    description="Get followers",
    responses=registry.get_exception_responses(
        service_exceptions.GetUserIdError,
        service_exceptions.UnauthorizedError,
    ),
)
async def get_followers(
    account_id: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
    limit: pydantic.PositiveInt = fastapi.Query(default=10, ge=1, le=100),
    offset: pydantic.NonNegativeInt = fastapi.Query(default=0),
) -> response.Response[pagination.Pagination[responses_schema.Follower]]:
    return response.Response[pagination.Pagination[responses_schema.Follower]](
        result=pagination.Pagination(
            url="",
            base_items=[],
            limit=limit,
            offset=offset,
            count=0,
        ),
    )


@router.get(
    "/follows",
    status_code=fastapi.status.HTTP_200_OK,
    description="Get follows",
    responses=registry.get_exception_responses(
        service_exceptions.GetUserIdError,
        service_exceptions.UnauthorizedError,
    ),
)
async def get_follows(
    follower_id: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
    limit: pydantic.PositiveInt = fastapi.Query(default=10, ge=1, le=100),
    offset: pydantic.NonNegativeInt = fastapi.Query(default=0),
) -> response.Response[pagination.Pagination[responses_schema.Follower]]:
    return response.Response[pagination.Pagination[responses_schema.Follower]](
        result=pagination.Pagination(
            url="",
            base_items=[],
            limit=limit,
            offset=offset,
            count=0,
        ),
    )


@router.delete(
    "/{followed_account_id}",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    description="Unfollow for account",
    responses=registry.get_exception_responses(
        service_exceptions.GetUserIdError,
        service_exceptions.UnauthorizedError,
    ),
)
async def unfollow(
    follower_id: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
) -> None:
    pass


@router.get(
    "/{account_id}/info",
    status_code=fastapi.status.HTTP_200_OK,
    responses=registry.get_exception_responses(
        service_exceptions.GetUserIdError,
        service_exceptions.UnauthorizedError,
        service_exceptions.UserNotFound,
    ),
)
async def get_account_info(
    account_id: pydantic.StrictStr = fastapi.Path(...),
    _: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> response.Response[responses_schema.AccountInfo]:
    result: get_feeds_model.GetAccountFeedsResponse = await mediator.send(
        get_feeds_model.GetAccountFeeds(
            account_id=account_id,
            limit=1,
            offset=0,
        ),
    )
    return response.Response(
        result=responses_schema.AccountInfo(
            account_id=account_id,
            followers_count=random.randint(0, 100),
            following_count=random.randint(0, 100),
            feeds_count=result.total_count,
        ),
    )
