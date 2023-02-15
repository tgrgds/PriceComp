from pydantic import BaseModel

class Product(BaseModel):
  name: str
  sku: str
  url: str
  price: float
  in_stock: bool

class ScraperData(BaseModel):
  totalHits: int
  hits: dict[str, int]
  products: list[Product]
