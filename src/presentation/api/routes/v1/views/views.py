import fastapi
import pydantic

from presentation.api import security
from presentation.api.schemas import requests as requests_schema

router = fastapi.APIRouter(prefix="/feeds/views")


@router.put(
    "/batch",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    description="View feed",
)
async def view_feed(
    body: requests_schema.ViewFeeds = fastapi.Body(...),
    account_id: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
) -> None:
    pass
