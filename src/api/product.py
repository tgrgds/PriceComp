from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from prisma.errors import UniqueViolationError

from src.prisma import prisma

class Product(BaseModel):
  # id: int
  sku: str
  price: float

router = APIRouter()

@router.get("/product/{sku}", tags=["product"])
async def get_product(sku: str):
  products = await prisma.product.find_many(
    where={
      "sku": { "search": sku }
    }
  )
  print("products", products)

  return products

@router.get("/product/search/{search}", tags=["product"])
async def search_products(search: str):
  # TODO: figure out how to sort by relevance
  # https://www.prisma.io/docs/concepts/components/prisma-client/filtering-and-sorting#sort-by-relevance-postgresql
  products = await prisma.product.find_many(
    where={
      "OR": [
        {
          "sku": { "contains": search }
        },
        {
          # i don't think we need a name field just for searching
          # as the name is contained in the url
          "url": { "contains": search.replace(" ", "-") }
        }
      ]
    }
  )

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