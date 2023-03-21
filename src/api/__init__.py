from fastapi import APIRouter

from src.api.product import router as productRouter
from src.api.scraper import router as scraperRouter
from src.api.auth import router as authRouter

api = APIRouter()
api.include_router(productRouter)
api.include_router(scraperRouter)
api.include_router(authRouter)

__all__ = ["api"]