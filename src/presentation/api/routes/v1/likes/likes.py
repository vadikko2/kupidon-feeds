import cqrs
import fastapi
import pydantic
from fastapi_app import response
from fastapi_app.exception_handlers import registry

from presentation import dependencies
from presentation.api import security
from presentation.api.schemas import pagination, responses as responses_schema
from service import exceptions as service_exceptions
from service.models.commands.likes import (
    like_feed as like_feed_model,
    unlike_feed as unlike_feed_model,
)
from service.models.queries.likes import get_likes as get_likes_model

router = fastapi.APIRouter(prefix="/feeds/likes")


@router.post(
    "/{feed_id}",
    status_code=fastapi.status.HTTP_201_CREATED,
    description="Like feed",
    responses=registry.get_exception_responses(
        service_exceptions.FeedNotFound,
        service_exceptions.GetUserIdError,
        service_exceptions.UnauthorizedError,
    ),
)
async def like(
    feed_id: pydantic.UUID4 = fastapi.Path(...),
    account_id: pydantic.StrictStr = fastapi.Depends(
        security.extract_account_id,
    ),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> response.Response[responses_schema.Like]:
    """
    # Like feed
    """
    result: like_feed_model.LikeFeedResponse = await mediator.send(
        like_feed_model.LikeFeed(
            feed_id=feed_id,
            account_id=account_id,
        ),
    )
    return response.Response(
        result=responses_schema.Like(
            account_id=result.like.account_id,
            feed_id=result.like.feed_id,
            liked_at=result.like.liked_at,
        ),
    )


@router.delete(
    "/{feed_id}",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    description="Unlike feed",
    responses=registry.get_exception_responses(
        service_exceptions.FeedNotFound,
        service_exceptions.GetUserIdError,
        service_exceptions.UnauthorizedError,
    ),
)
async def unlike(
    feed_id: pydantic.UUID4 = fastapi.Path(...),
    account_id: pydantic.StrictStr = fastapi.Depends(
        security.extract_account_id,
    ),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> None:
    """
    # Unlike feed
    """
    await mediator.send(
        unlike_feed_model.UnlikeFeed(
            feed_id=feed_id,
            account_id=account_id,
        ),
    )


@router.get(
    "/{feed_id}",
    status_code=fastapi.status.HTTP_200_OK,
    description="Get likes",
    responses=registry.get_exception_responses(
        service_exceptions.FeedNotFound,
        service_exceptions.GetUserIdError,
        service_exceptions.UnauthorizedError,
    ),
)
async def get_likes(
    feed_id: pydantic.UUID4 = fastapi.Path(...),
    _: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
    limit: pydantic.PositiveInt = fastapi.Query(default=10, ge=1, le=100),
    offset: pydantic.NonNegativeInt = fastapi.Query(default=0),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> response.Response[pagination.Pagination[responses_schema.Like]]:
    """
    # Get likes for feed
    """
    result: get_likes_model.GetLikesResponse = await mediator.send(
        get_likes_model.GetLikes(
            feed_id=feed_id,
            limit=limit,
            offset=offset,
        ),
    )
    return response.Response[pagination.Pagination[responses_schema.Like]](
        result=pagination.Pagination[responses_schema.Like](
            url="",
            base_items=[
                responses_schema.Like(
                    account_id=like.account_id,
                    feed_id=like.feed_id,
                    liked_at=like.liked_at,
                )
                for like in result.likes
            ],
            limit=result.limit,
            offset=result.offset,
            count=result.total_count,
        ),
    )
