from fastapi import APIRouter

from src.api.product import router as productRouter

api = APIRouter()
api.include_router(productRouter)

__all__ = ["api"]