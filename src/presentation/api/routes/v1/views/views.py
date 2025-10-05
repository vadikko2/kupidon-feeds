import fastapi
import pydantic

from presentation.api import security

router = fastapi.APIRouter(prefix="/feeds/views")


@router.put(
    "/{feed_id}",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    description="View feed",
)
async def view_feed(
    feed_id: pydantic.UUID4 = fastapi.Path(...),
    account_id: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
) -> None:
    pass
