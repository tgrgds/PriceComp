from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.api import api
from src.prisma import prisma

app = FastAPI(
  title="PriceComp",
  version="0.0.1"
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"], # TODO: set specific origins!!
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)

app.include_router(api, prefix="/api")

@app.on_event("startup")
async def startup():
  await prisma.connect()

@app.on_event("shutdown")
async def shutdown():
  await prisma.disconnect()

@app.get("/")
def read_root():
  return {"version": "0.0.1"}

# class Item(BaseModel):
#   name: str
#   price: float
#   is_offer: Union[bool, None] = None

# @app.get("/")
# def read_root():
#   return {"Hello":"World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#   return {"item_id": item_id, "q": q}

# @app.put("/items/{item_id}")
# def update_item(item_id: int, item: Item):
#   return {"item_price": item.price, "item_id": item_id}
