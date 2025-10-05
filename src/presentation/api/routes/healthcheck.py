import functools
import logging

import fastapi
import orjson
import redis.asyncio as rc
from fastapi import responses

from infrastructure.cache import redis
from presentation.api.schemas import healthcheck as healthcheck_response

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()


@router.get(
    "/healthcheck",
    status_code=fastapi.status.HTTP_200_OK,
    response_model=healthcheck_response.Healthcheck,
    responses={
        fastapi.status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Service Unavailable",
        },
        fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal Server Error",
        },
    },
)
async def healthcheck(
    redis_client: rc.Redis = fastapi.Depends(
        redis.RedisClientFactory(),
    ),
):
    """
    # Health checks
    """
    checks = {
        "redis": functools.partial(redis_client.ping),
    }
    check_results = []
    healthy = True
    for name, check in checks.items():
        try:
            await check()
            check_results.append(healthcheck_response.Check(name=name, healthy=True))
        except Exception as error:
            healthy = False
            check_results.append(
                healthcheck_response.Check(name=name, healthy=False, error=str(error)),
            )
            logger.error(f"{name} is unhealthy: {error}")

    status_code = (
        fastapi.status.HTTP_200_OK
        if healthy
        else fastapi.status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return responses.JSONResponse(
        status_code=status_code,
        content=orjson.loads(
            healthcheck_response.Healthcheck(
                checks=check_results,
            ).model_dump_json(),
        ),
    )
