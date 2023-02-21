from pydantic import BaseModel
from typing import Union

class Product(BaseModel):
  id: Union[str, None] # combination of store_sku
  name: str
  sku: str
  url: str
  price: float
  in_stock: bool

class ScraperData(BaseModel):
  hits: int
  products: list[Product]
