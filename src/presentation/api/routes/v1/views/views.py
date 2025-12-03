import cqrs
import fastapi
import pydantic

from presentation import dependencies
from presentation.api import limiter, security, settings
from presentation.api.schemas import requests as requests_schema
from service.models.commands.views import view_feeds as view_feeds_model

router = fastapi.APIRouter(prefix="/feeds/views")


async def _process_views(
    feed_ids: list[pydantic.UUID4],
    account_id: str,
    mediator: cqrs.RequestMediator,
) -> None:
    """
    Background task to process views
    """
    await mediator.send(
        view_feeds_model.ViewFeeds(
            feed_ids=feed_ids,
            account_id=account_id,
        ),
    )


@router.put(
    "/batch",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    description="View feeds (idempotent, background processing)",
)
@limiter.limiter.limit(settings.api_settings.max_requests_per_ip_limit)
async def view_feeds(
    request: fastapi.Request,
    body: requests_schema.ViewFeeds = fastapi.Body(...),
    account_id: pydantic.StrictStr = fastapi.Depends(security.extract_account_id),
    background_tasks: fastapi.BackgroundTasks = fastapi.BackgroundTasks(),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> None:
    """
    Batch view feeds endpoint.
    Executes in background - does not guarantee processing.
    Idempotent - same user can view same feed only once.
    """
    background_tasks.add_task(
        _process_views,
        feed_ids=body.feed_ids,
        account_id=account_id,
        mediator=mediator,
    )
