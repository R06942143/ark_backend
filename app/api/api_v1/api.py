from fastapi import APIRouter

from app.api.api_v1.endpoints import login, users, nft, line, joyso, linepay

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/user", tags=["user"])
api_router.include_router(nft.router, prefix="/nft", tags=["nft"])
api_router.include_router(line.router, prefix="/line", tags=["line"])
api_router.include_router(linepay.router, prefix="/linepay", tags=["linepay"])