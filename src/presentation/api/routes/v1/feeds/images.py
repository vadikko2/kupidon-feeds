import uuid

import fastapi
import pydantic
from fastapi_app import response

from presentation.api import security
from presentation.api.schemas import responses as responses_schema

router = fastapi.APIRouter(prefix="/feeds/images")


@router.post(
    "",
    status_code=fastapi.status.HTTP_201_CREATED,
    description="Upload images",
)
async def upload_image(
    image: fastapi.UploadFile = fastapi.File(...),
    account_id: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
) -> response.Response[responses_schema.Image]:
    return response.Response(
        result=responses_schema.Image(
            uuid=uuid.uuid4(),
            url="https://example.com/image.jpg",
            blurhash="",
        ),
    )
