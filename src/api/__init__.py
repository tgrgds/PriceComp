from fastapi import APIRouter

from src.api.product import router as productRouter
from src.api.scraper import router as scraperRouter

api = APIRouter()
api.include_router(productRouter)
api.include_router(scraperRouter)

__all__ = ["api"]