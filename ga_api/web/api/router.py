from fastapi.routing import APIRouter

from ga_api.web.api import (
    availability,
    block,
    dummy,
    echo,
    mail,
    monitoring,
    professionals,
    schedule,
    speciality,
    users,
)

api_router = APIRouter()

admin_router = APIRouter(prefix="/admin")

admin_router.include_router(patients.router, prefix="/patients", tags=["admin", "patients"])

admin_router.include_router(block.router, prefix="/blocks", tags=["admin", "blocks"])

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

admin_router.include_router(
    schedule.admin_router,
    prefix="/schedule",
    tags=["admin", "schedule"],
)

admin_router.include_router(
    speciality.admin_router,
    prefix="/speciality",
    tags=["admin", "speciality"],
)

api_router.include_router(admin_router)
api_router.include_router(monitoring.router)
api_router.include_router(users.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(mail.router, prefix="/mail", tags=["mail"])
api_router.include_router(
    professionals.router,
    prefix="/professionals",
    tags=["professionals"],
)
api_router.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
