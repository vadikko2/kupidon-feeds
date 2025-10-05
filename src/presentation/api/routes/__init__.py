import fastapi

from presentation.api.routes import healthcheck, v1

api_router = fastapi.APIRouter(prefix="/api")

api_router.include_router(
    healthcheck.router,
    prefix="",
    tags=["Healthcheck"],
)
api_router.include_router(v1.v1_router)
