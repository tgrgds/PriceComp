from fastapi import APIRouter, HTTPException, Depends
from typing import Union
from pydantic import BaseModel
from prisma.errors import UniqueViolationError
import re

from src.prisma import prisma
from src.auth import api_key_auth
from src.type import SiteName

class Product(BaseModel):
  # id: int
  sku: str
  price: float

router = APIRouter()

# TODO: merge this with /product/{store}/search with "store" query param
@router.get("/product/search/{search}", dependencies=[Depends(api_key_auth)], tags=["product"])
async def search_products(search: str, strict: bool = False, store: Union[SiteName, None] = None):
  # TODO: figure out how to sort by relevance
  # https://www.prisma.io/docs/concepts/components/prisma-client/filtering-and-sorting#sort-by-relevance-postgresql

  # Default, non-strict search
  # loosely compares searchterm with sku and the name contained in the url
  query = {
    "OR": [
      {
        "sku": { "contains": search },
      },
      {
        # i don't think we need a name field just for searching
        # as the name is contained in the url
        "url": { "contains": search.replace(" ", "-") },
      }
    ]
  }

  if strict:
    query = {
      "sku_trunc": re.sub(r'[^a-zA-Z0-9]', '', search),
    }

  products = await prisma.product.find_many(where=query, order={"price": "asc"})

  return products

# same as above but with specific "store" param
# TODO: merge with above func with a query param instead
@router.get("/product/{store}/search/{search}", dependencies=[Depends(api_key_auth)], tags=["product"])
async def search_store_products(search: str, store: SiteName, strict: bool = False):
  query = {
    "OR": [
      {
        "sku": { "contains": search },
      },
      {
        "url": { "contains": search.replace(" ", "-") },
      }
    ]
  }

  if strict:
    query = { 
      "sku": search,
    }

  products = await prisma.product.find_many(
    where={
      **query,
      "store_id": store
    },
    order={
      "price": "asc"
    }
  )

  return products

# Get all products from the given store
# Useful for making reports
@router.get("/product/{store}/all", dependencies=[Depends(api_key_auth)], tags=["product"])
async def get_all_products(store: SiteName):
  products = await prisma.product.find_many(
    where={
      "store_id": store
    }
  )

  return products

# @router.post("/product/", tags=["product"])
# async def new_product(product: Product):
#   try:
#     product = await prisma.product.create({
#       "sku": product.sku,
#       "price": product.price
#     })

#   except UniqueViolationError:
#     raise HTTPException(status_code=400, detail="A product with this SKU already exists.")

#   return product