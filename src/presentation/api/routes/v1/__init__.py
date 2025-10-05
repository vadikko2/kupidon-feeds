import fastapi

from presentation.api.routes.v1 import feeds, followers, likes

v1_router = fastapi.APIRouter(prefix="/v1")

v1_router.include_router(feeds.feeds_router)
v1_router.include_router(followers.followers_router)
v1_router.include_router(likes.likes_router)

__all__ = ["v1_router"]
