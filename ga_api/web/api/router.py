from fastapi.routing import APIRouter

from ga_api.web.api import (
    availability,
    dummy,
    echo,
    mail,
    monitoring,
    professionals,
    users,
)

api_router = APIRouter()

admin_router = APIRouter(prefix="/admin")
admin_router.include_router(
    availability.admin_router,
    prefix="/availability",
    tags=["admin", "availability"],
)
admin_router.include_router(
    professionals.admin_router,
    prefix="/professionals",
    tags=["admin", "professionals"],
)

api_router.include_router(admin_router)
api_router.include_router(monitoring.router)
api_router.include_router(users.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(mail.router, prefix="/mail", tags=["mail"])
