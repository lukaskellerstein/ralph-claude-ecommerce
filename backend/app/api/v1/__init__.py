from fastapi import APIRouter

from app.api.v1.categories import router as categories_router
from app.api.v1.products import router as products_router

api_router = APIRouter()

api_router.include_router(categories_router, prefix="/categories", tags=["categories"])
api_router.include_router(products_router, prefix="/products", tags=["products"])
