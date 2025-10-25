import datetime
import random
import uuid

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
from service.models.commands import post_feed as post_feed_model

router = fastapi.APIRouter(prefix="/feeds")

print(
    registry.get_exception_responses(
        service_exceptions.FeedAlreadyExists,
        service_exceptions.GetUserIdError,
        service_exceptions.UnauthorizedError,
        service_exceptions.ImageAlreadyBoundToFeed,
        service_exceptions.ImageNotFound,
    ),
)


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
async def post_feed(
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
        result=responses_schema.Feed(
            uuid=result.feed.feed_id,
            account_id=account_id,
            has_followed=False,
            created_at=result.feed.created_at,
            updated_at=result.feed.updated_at,
            text=body.text,
            images=[
                responses_schema.OrderedImage(
                    image=responses_schema.Image(
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
async def get_feeds(
    feed_id: list[pydantic.UUID4] = fastapi.Query(
        min_length=1,
        max_length=100,
    ),
    _: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
) -> response.Response[responses_schema.Feeds]:
    return response.Response[responses_schema.Feeds](
        result=responses_schema.Feeds(
            items=[
                responses_schema.Feed(
                    uuid=_id,
                    account_id=f"fake-account-{random.randint(1, 10_000)}",
                    has_followed=bool(random.randint(0, 1)),
                    created_at=datetime.datetime.now()
                    - datetime.timedelta(days=random.randint(1, 3_000)),
                    updated_at=None,
                    text="",
                    images=[
                        responses_schema.OrderedImage(
                            image=responses_schema.Image(
                                uuid=uuid.uuid4(),
                                url="https://s3.twcstorage.ru/baa7cf79-ml-env-s3/profiles/mock_female.jpg",
                                blurhash="LRNJ^29G%g%NE1Mx_NRiE1ogofV@",
                            ),
                            order=0,
                        )
                        for _ in range(random.randint(1, 10))
                    ],
                    likes_count=random.randint(0, 1_000_000),
                    views_count=random.randint(0, 1_000_000),
                )
                for _id in feed_id
            ],
        ),
    )


@router.get(
    "/{account_id}",
    status_code=fastapi.status.HTTP_200_OK,
    description="Get account feeds",
)
async def get_account_feeds(
    account_id: pydantic.StrictStr = fastapi.Path(...),
    _: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
    limit: pydantic.PositiveInt = fastapi.Query(default=10, ge=1, le=100),
    offset: pydantic.NonNegativeInt = fastapi.Query(default=0),
) -> response.Response[pagination.Pagination[responses_schema.Feed]]:
    return response.Response[pagination.Pagination[responses_schema.Feed]](
        result=pagination.Pagination(
            url="",
            base_items=[
                responses_schema.Feed(
                    uuid=uuid.uuid4(),
                    account_id=account_id,
                    has_followed=bool(random.randint(0, 1)),
                    created_at=datetime.datetime.now()
                    - datetime.timedelta(days=random.randint(1, 3_000)),
                    updated_at=None,
                    text="",
                    images=[
                        responses_schema.OrderedImage(
                            image=responses_schema.Image(
                                uuid=uuid.uuid4(),
                                url="https://s3.twcstorage.ru/baa7cf79-ml-env-s3/profiles/mock_female.jpg",
                                blurhash="LRNJ^29G%g%NE1Mx_NRiE1ogofV@",
                            ),
                            order=0,
                        )
                        for _ in range(random.randint(1, 10))
                    ],
                    likes_count=random.randint(0, 1_000_000),
                    views_count=random.randint(0, 1_000_000),
                )
                for _ in range(limit)
            ],
            limit=limit,
            offset=offset,
            count=0,
        ),
    )


@router.patch(
    "/{feed_id}",
    status_code=fastapi.status.HTTP_200_OK,
    description="Update feed",
)
async def patch_feed(
    feed_id: pydantic.UUID4 = fastapi.Path(...),
    body: requests_schema.UpdateFeed = fastapi.Body(...),
    account_id: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
) -> response.Response[responses_schema.Feed]:
    return response.Response(
        result=responses_schema.Feed(
            uuid=feed_id,
            account_id=account_id,
            has_followed=bool(random.randint(0, 1)),
            created_at=datetime.datetime.now()
            - datetime.timedelta(days=random.randint(1, 3_000)),
            updated_at=datetime.datetime.now(),
            text=body.text,
            images=[
                responses_schema.OrderedImage(
                    image=responses_schema.Image(
                        uuid=image_uuid,
                        url="https://s3.twcstorage.ru/baa7cf79-ml-env-s3/profiles/mock_female.jpg",
                        blurhash="LRNJ^29G%g%NE1Mx_NRiE1ogofV@",
                    ),
                    order=i,
                )
                for i, image_uuid in enumerate(body.images)
            ],
            likes_count=random.randint(0, 1_000_000),
            views_count=random.randint(0, 1_000_000),
        ),
    )


@router.delete(
    "/{feed_id}",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    description="Delete feed",
)
async def delete_feed(
    feed_id: pydantic.UUID4 = fastapi.Path(...),
    account_id: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
) -> None:
    pass
