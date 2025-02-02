from fastapi import APIRouter

from api.app.podnotes import router as podnotes
# from app.core.config import settings

api_router = APIRouter()
api_router.include_router(podnotes)


# if settings.ENVIRONMENT == "local":
# api_router.include_router(private.router)