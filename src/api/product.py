from typing import Union
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.prisma import prisma

class Product(BaseModel):
  # id: int
  sku: str
  price: float

router = APIRouter()

@router.get("/product/", tags=["product"])
async def read_users():
  products = await prisma.product.find_many()
  print("products", products)

  return products

@router.post("/product/", tags=["product"])
async def new_user(product: Product):
  product = await prisma.product.create({
    "sku": product.sku,
    "price": product.price
  })

  return product