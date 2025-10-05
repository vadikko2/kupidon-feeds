import fastapi

from presentation.api.routes import v1

api_router = fastapi.APIRouter(prefix="/api")

api_router.include_router(v1.v1_router)


__all__ = ["api_router"]
