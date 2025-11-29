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
from service.models.commands.followers import (
    follow as follow_model,
    unfollow as unfollow_model,
)
from service.models.queries.followers import (
    get_account_info as get_account_info_model,
    get_followers as get_followers_model,
    get_following as get_following_model,
)

router = fastapi.APIRouter(prefix="/followers")


@router.post(
    "",
    status_code=fastapi.status.HTTP_201_CREATED,
    description="Follow for account",
    responses=registry.get_exception_responses(
        service_exceptions.GetUserIdError,
        service_exceptions.UnauthorizedError,
        service_exceptions.UserNotFound,
        service_exceptions.CannotFollowSelf,
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
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> response.Response[pagination.Pagination[responses_schema.Follower]]:
    """
    # Get followers
    """
    result: get_followers_model.GetFollowersResponse = await mediator.send(
        get_followers_model.GetFollowers(
            account_id=account_id,
            limit=limit,
            offset=offset,
        ),
    )

    return response.Response[pagination.Pagination[responses_schema.Follower]](
        result=pagination.Pagination[responses_schema.Follower](
            url="",
            base_items=[
                responses_schema.Follower(
                    follower=follower.follower,
                    follow_for=follower.follow_for,
                    followed_at=follower.followed_at,
                )
                for follower in result.followers
            ],
            limit=limit,
            offset=offset,
            count=result.total_count,
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
    account_id: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
    limit: pydantic.PositiveInt = fastapi.Query(default=10, ge=1, le=100),
    offset: pydantic.NonNegativeInt = fastapi.Query(default=0),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> response.Response[pagination.Pagination[responses_schema.Follower]]:
    """
    # Get follows (following)
    """
    result: get_following_model.GetFollowingResponse = await mediator.send(
        get_following_model.GetFollowing(
            account_id=account_id,
            limit=limit,
            offset=offset,
        ),
    )

    return response.Response[pagination.Pagination[responses_schema.Follower]](
        result=pagination.Pagination[responses_schema.Follower](
            url="",
            base_items=[
                responses_schema.Follower(
                    follower=follower.follower,
                    follow_for=follower.follow_for,
                    followed_at=follower.followed_at,
                )
                for follower in result.following
            ],
            limit=limit,
            offset=offset,
            count=result.total_count,
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
    followed_account_id: pydantic.StrictStr = fastapi.Path(...),
    follower_id: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> None:
    await mediator.send(
        unfollow_model.Unfollow(
            follower=follower_id,
            follow_for=followed_account_id,
        ),
    )


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
    result: get_account_info_model.GetAccountInfoResponse = await mediator.send(
        get_account_info_model.GetAccountInfo(
            account_id=account_id,
        ),
    )
    return response.Response(
        result=responses_schema.AccountInfo(
            account_id=result.account_id,
            followers_count=result.followers_count,
            following_count=result.following_count,
            feeds_count=result.feeds_count,
        ),
    )
