import logging
from contextlib import asynccontextmanager
from logging import config

import dotenv
import fastapi
import fastapi_app
from fastapi_app import logging as fastapi_logging

import settings
from infrastructure.persistent.postgres import connection as postgres_connection
from presentation.api import errors, limiter, routes
from presentation.api.routes import healthcheck

dotenv.load_dotenv()

log_settings = settings.Logging()
app_settings = settings.App()

log_config = fastapi_logging.generate_log_config(
    logging_level=log_settings.LEVEL,
    serialize=log_settings.SERIALIZE,
    app_name=app_settings.NAME,
    app_version=settings.VERSION,
)

config.dictConfig(log_config)
logging.getLogger("uvicorn").setLevel(logging.ERROR)
logging.getLogger("uvicorn.access").setLevel(logging.ERROR)
logging.getLogger("uvicorn.asgi").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("multipart").setLevel(logging.ERROR)
logging.getLogger("python_multipart").setLevel(logging.ERROR)
logging.getLogger("cqrs").setLevel(logging.ERROR)
logging.getLogger("faker").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("httpx_retries").setLevel(logging.ERROR)


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    await postgres_connection.init_pool()
    try:
        yield
    finally:
        await postgres_connection.close_pool()


app = fastapi_app.create(
    debug=app_settings.DEBUG,
    title=app_settings.NAME,
    version=settings.VERSION,
    description="Feeds API",
    env_title=app_settings.ENV,
    query_routers=[
        routes.api_router,
        healthcheck.router,
    ],
    exception_handlers=errors.handlers,
    cors_enable=True,
    log_config=log_config,
    lifespan_handler=lifespan,
)
# Rate Limitation
app.state.limiter = limiter.limiter
