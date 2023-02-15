from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from prisma.errors import UniqueViolationError

from src.prisma import prisma

class Product(BaseModel):
  # id: int
  sku: str
  price: float

router = APIRouter()

@router.get("/product/", tags=["product"])
async def read_products():
  products = await prisma.product.find_many()
  print("products", products)

  return products

@router.post("/product/", tags=["product"])
async def new_product(product: Product):
  try:
    product = await prisma.product.create({
      "sku": product.sku,
      "price": product.price
    })

  except UniqueViolationError:
    raise HTTPException(status_code=400, detail="A product with this SKU already exists.")

  return product