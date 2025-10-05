import datetime

import fastapi
import pydantic
from fastapi_app import response

from presentation.api import security
from presentation.api.schemas import pagination, responses as responses_schema

router = fastapi.APIRouter(prefix="/feeds/likes")


@router.post(
    "/{feed_id}",
    status_code=fastapi.status.HTTP_201_CREATED,
    description="Like feed",
)
async def like(
    feed_id: pydantic.UUID4 = fastapi.Path(...),
    target_account_id: pydantic.StrictStr = fastapi.Depends(
        security.extract_account_id,
    ),
) -> response.Response[responses_schema.Like]:
    return response.Response(
        result=responses_schema.Like(
            account_id=target_account_id,
            feed_id=feed_id,
            liked_at=datetime.datetime.now(),
        ),
    )


@router.delete(
    "/{feed_id}",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    description="Unlike feed",
)
async def unlike(
    feed_id: pydantic.UUID4 = fastapi.Path(...),
    target_account_id: pydantic.StrictStr = fastapi.Depends(
        security.extract_account_id,
    ),
) -> None:
    pass


@router.get(
    "/{feed_id}",
    status_code=fastapi.status.HTTP_200_OK,
    description="Get likes",
)
async def get_likes(
    feed_id: pydantic.UUID4 = fastapi.Path(...),
    account_id: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
    limit: pydantic.PositiveInt = fastapi.Query(default=10, ge=1, le=100),
    offset: pydantic.NonNegativeInt = fastapi.Query(default=0),
) -> response.Response[pagination.Pagination[responses_schema.Like]]:
    return response.Response[pagination.Pagination[responses_schema.Like]](
        result=pagination.Pagination(
            url="",
            base_items=[],
            limit=limit,
            offset=offset,
            count=0,
        ),
    )
