import fastapi

from presentation.api.routes.v1.likes import likes

likes_router = fastapi.APIRouter()

likes_router.include_router(likes.router, tags=["Likes"])

__all__ = ["likes_router"]
