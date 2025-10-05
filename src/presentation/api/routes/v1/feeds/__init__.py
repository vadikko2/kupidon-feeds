import fastapi

from presentation.api.routes.v1.feeds import images, feeds

feeds_router = fastapi.APIRouter()

feeds_router.include_router(images.router, tags=["Images"])
feeds_router.include_router(feeds.router, tags=["Feeds"])

__all__ = ["feeds_router"]
