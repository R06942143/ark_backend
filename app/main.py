from sqlalchemy import null
from starlette.types import Message
from fastapi import FastAPI, Request, Depends
from starlette.middleware.cors import CORSMiddleware
import base64
import json
import dataset
from datetime import datetime
from app.crud.crud_user import user
from app.api.api_v1.api import api_router
from app.core.config import settings
from app.api import deps
from sqlalchemy.orm import Session


app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app.include_router(api_router, prefix=settings.API_V1_STR)
