import cqrs
import fastapi
import pydantic
from fastapi_app import response
from fastapi_app.exception_handlers import registry

from presentation import dependencies
from presentation.api import security
from presentation.api.schemas import responses as responses_schema
from service import exceptions as service_exceptions
from service.models.commands.images import upload_image as upload_image_model

router = fastapi.APIRouter(prefix="/feeds/images")


@router.post(
    "",
    status_code=fastapi.status.HTTP_201_CREATED,
    responses=registry.get_exception_responses(
        service_exceptions.GetUserIdError,
        service_exceptions.UnauthorizedError,
        service_exceptions.ImageAlreadyExists,
    ),
)
async def upload_image(
    image: fastapi.UploadFile = fastapi.File(...),
    account_id: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> response.Response[responses_schema.Image]:
    """
    # Upload image
    """
    filename = image.filename
    image_bytes = await image.read()

    result: upload_image_model.UploadImageResponse = await mediator.send(
        upload_image_model.UploadImage(
            uploader=account_id,
            image=image_bytes,
            filename=filename,
        ),
    )

    return response.Response(
        result=responses_schema.Image(
            uuid=result.image.image_id,
            url=result.image.url,
            blurhash=result.image.blurhash,
        ),
    )
