import fastapi

from presentation.api.routes.v1.views import views

views_router = fastapi.APIRouter()

views_router.include_router(views.router, tags=["Views"])

__all__ = ["views_router"]
