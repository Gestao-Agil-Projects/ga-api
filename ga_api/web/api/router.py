from fastapi.routing import APIRouter

from ga_api.web.api import block, dummy, echo, mail, monitoring, users

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(users.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(mail.router, prefix="/mail", tags=["mail"])
api_router.include_router(block.router, prefix="/admin/blocks", tags=["blocks"])
