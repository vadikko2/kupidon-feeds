import fastapi

from presentation.api.routes.v1.followers import followers

followers_router = fastapi.APIRouter()

followers_router.include_router(followers.router, tags=["Followers"])

__all__ = ["followers_router"]
