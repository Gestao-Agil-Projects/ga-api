from fastapi.routing import APIRouter

from ga_api.web.api import availability, block, dummy, echo, mail, monitoring, users
from ga_api.web.api.admin import admin_views
from ga_api.web.api.scheduling import scheduling_views

api_router = APIRouter()

admin_router = APIRouter(prefix="/admin")

admin_router.include_router(block.router, prefix="/blocks", tags=["admin", "blocks"])

admin_router.include_router(
    availability.admin_router,
    prefix="/availability",
    tags=["admin", "availability"],
)

api_router.include_router(
    scheduling_views.scheduling_router,
    prefix="/scheduling",
    tags=["Scheduling"],
)

admin_router.include_router(admin_views.admin_router)

api_router.include_router(admin_router)
api_router.include_router(monitoring.router)
api_router.include_router(users.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(mail.router, prefix="/mail", tags=["mail"])
