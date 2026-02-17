import cqrs
import fastapi
import pydantic
from fastapi_app import response
from fastapi_app.exception_handlers import registry

from presentation import dependencies
from presentation.api import limiter, security, settings
from presentation.api.schemas import (
    pagination,
    requests as requests_schema,
    responses as responses_schema,
)
from service import exceptions as service_exceptions
from service.models.commands.feeds import (
    delete_feed as delete_feed_model,
    post_feed as post_feed_model,
    update_feed as update_feed_model,
)
from service.models.queries.feeds import get_feeds as get_feeds_model

router = fastapi.APIRouter(prefix="/feeds")


@router.post(
    "",
    status_code=fastapi.status.HTTP_201_CREATED,
    responses=registry.get_exception_responses(
        service_exceptions.FeedAlreadyExists,
        service_exceptions.GetUserIdError,
        service_exceptions.UnauthorizedError,
        service_exceptions.ImageAlreadyBoundToFeed,
        service_exceptions.ImageNotFound,
    ),
)
@limiter.limiter.limit(settings.api_settings.max_requests_per_ip_limit)
async def post_feed(
    request: fastapi.Request,
    body: requests_schema.PostFeed = fastapi.Body(...),
    account_id: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> response.Response[responses_schema.Feed]:
    """
    # Create feed
    """
    result: post_feed_model.PostFeedResponse = await mediator.send(
        post_feed_model.PostFeed(
            account_id=account_id,
            text=body.text,
            images=body.images,
        ),
    )
    return response.Response(
        result=responses_schema.Feed.model_construct(
            uuid=result.feed.feed_id,
            account_id=account_id,
            has_followed=False,
            created_at=result.feed.created_at,
            updated_at=result.feed.updated_at,
            text=body.text,
            images=[
                responses_schema.OrderedImage.model_construct(
                    image=responses_schema.Image.model_construct(
                        uuid=image.image_id,
                        url=image.url,
                        blurhash=image.blurhash,
                    ),
                    order=image.order,
                )
                for image in result.feed.images
            ],
            likes_count=result.feed.likes_count,
            views_count=result.feed.views_count,
        ),
    )


@router.get(
    "",
    status_code=fastapi.status.HTTP_200_OK,
    description="Get feeds",
)
@limiter.limiter.limit(settings.api_settings.max_requests_per_ip_limit)
async def get_feeds(
    request: fastapi.Request,
    feed_id: list[pydantic.UUID4] = fastapi.Query(
        min_length=1,
        max_length=100,
    ),
    account_id: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> response.Response[responses_schema.Feeds]:
    """
    # Get feeds by ids
    """
    result: get_feeds_model.GetFeedsResponse = await mediator.send(
        get_feeds_model.GetFeeds(feed_ids=feed_id, current_account_id=account_id),
    )

    return response.Response[responses_schema.Feeds](
        result=responses_schema.Feeds.model_construct(
            items=[
                responses_schema.Feed.model_construct(
                    uuid=feed.feed_id,
                    account_id=feed.account_id,
                    has_followed=feed.has_followed,
                    has_liked=feed.has_liked,
                    created_at=feed.created_at,
                    updated_at=feed.updated_at,
                    text=feed.text,
                    images=[
                        responses_schema.OrderedImage.model_construct(
                            image=responses_schema.Image.model_construct(
                                uuid=image.image_id,
                                url=image.url,
                                blurhash=image.blurhash,
                            ),
                            order=image.order,
                        )
                        for image in feed.images
                    ],
                    likes_count=feed.likes_count,
                    views_count=feed.views_count,
                )
                for feed in result.feeds
            ],
        ),
    )


@router.get(
    "/{account_id}",
    status_code=fastapi.status.HTTP_200_OK,
    description="Get account feeds",
    responses=registry.get_exception_responses(
        service_exceptions.GetUserIdError,
        service_exceptions.UnauthorizedError,
    ),
)
@limiter.limiter.limit(settings.api_settings.max_requests_per_ip_limit)
async def get_account_feeds(
    request: fastapi.Request,
    account_id: pydantic.StrictStr = fastapi.Path(...),
    current_account_id: pydantic.StrictStr = fastapi.Depends(
        security.extract_account_id,
    ),
    limit: pydantic.PositiveInt = fastapi.Query(default=10, ge=1, le=100),
    offset: pydantic.NonNegativeInt = fastapi.Query(default=0),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> response.Response[pagination.Pagination[responses_schema.Feed]]:
    """
    # Get account feeds
    """
    result: get_feeds_model.GetAccountFeedsResponse = await mediator.send(
        get_feeds_model.GetAccountFeeds(
            account_id=account_id,
            current_account_id=current_account_id,
            limit=limit,
            offset=offset,
        ),
    )

    return response.Response[pagination.Pagination[responses_schema.Feed]](
        result=pagination.Pagination[responses_schema.Feed].model_construct(
            url="",
            base_items=[
                responses_schema.Feed.model_construct(
                    uuid=feed.feed_id,
                    account_id=account_id,
                    has_followed=feed.has_followed,
                    has_liked=feed.has_liked,
                    created_at=feed.created_at,
                    updated_at=feed.updated_at,
                    text=feed.text,
                    images=[
                        responses_schema.OrderedImage.model_construct(
                            image=responses_schema.Image.model_construct(
                                uuid=image.image_id,
                                url=image.url,
                                blurhash=image.blurhash,
                            ),
                            order=image.order,
                        )
                        for image in feed.images
                    ],
                    likes_count=feed.likes_count,
                    views_count=feed.views_count,
                )
                for feed in result.feeds
            ],
            limit=limit,
            offset=offset,
            count=result.total_count,
        ),
    )


@router.patch(
    "/{feed_id}",
    status_code=fastapi.status.HTTP_200_OK,
    description="Update feed",
    responses=registry.get_exception_responses(
        service_exceptions.GetUserIdError,
        service_exceptions.UnauthorizedError,
        service_exceptions.FeedNotFound,
        service_exceptions.UserDoesNotOwnFeed,
    ),
)
@limiter.limiter.limit(settings.api_settings.max_requests_per_ip_limit)
async def patch_feed(
    request: fastapi.Request,
    feed_id: pydantic.UUID4 = fastapi.Path(...),
    body: requests_schema.UpdateFeed = fastapi.Body(...),
    account_id: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> response.Response[responses_schema.Feed]:
    """
    # Update feed
    """
    result: update_feed_model.UpdateFeedResponse = await mediator.send(
        update_feed_model.UpdateFeed(
            feed_id=feed_id,
            account_id=account_id,
            text=body.text,
            images=body.images,
        ),
    )
    return response.Response(
        result=responses_schema.Feed.model_construct(
            uuid=result.feed.feed_id,
            account_id=result.feed.account_id,
            has_followed=result.feed.has_followed,
            created_at=result.feed.created_at,
            updated_at=result.feed.updated_at,
            text=body.text,
            images=[
                responses_schema.OrderedImage.model_construct(
                    image=responses_schema.Image.model_construct(
                        uuid=image.image_id,
                        url=image.url,
                        blurhash=image.blurhash,
                    ),
                    order=image.order,
                )
                for image in result.feed.images
            ],
            likes_count=result.feed.likes_count,
            views_count=result.feed.views_count,
        ),
    )


@router.delete(
    "/{feed_id}",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    description="Delete feed (idempotent: no error if feed does not exist)",
    responses=registry.get_exception_responses(
        service_exceptions.GetUserIdError,
        service_exceptions.UnauthorizedError,
        service_exceptions.UserDoesNotOwnFeed,
    ),
)
@limiter.limiter.limit(settings.api_settings.max_requests_per_ip_limit)
async def delete_feed(
    request: fastapi.Request,
    feed_id: pydantic.UUID4 = fastapi.Path(...),
    account_id: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> None:
    """
    # Delete feed
    """
    await mediator.send(
        delete_feed_model.DeleteFeed(
            feed_id=feed_id,
            account_id=account_id,
        ),
    )
