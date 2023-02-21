from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from enum import Enum
from json import dump

from src.prisma import prisma
from src.scraper import Scraper
from src.scraper.better import BetterScraper
from src.scraper.mannys import MannysScraper

router = APIRouter()

class SiteName(str, Enum):
  better = "better"
  mannys = "mannys"

@router.post("/scraper/{site_name}", tags=["scraper"])
async def scrape_one(site_name: SiteName):
  scraper: Scraper = None

  # todo: make this better when more scrapers come in
  if site_name == SiteName.better:
    scraper = BetterScraper

  elif site_name == SiteName.mannys:
    scraper = MannysScraper

  else:
    raise HTTPException(status_code=400, detail="The requested site does not exist.")
  
  # TODO: exception handling
  for chunk in scraper.scrape_all():
    async with prisma.batch_() as batcher:
      for product in chunk["products"]:
        data = {
          "id": f"{site_name.value}_{product['sku'].replace(' ', '-').lower()}",
          "store_id": site_name.value,
          "sku": product["sku"],
          "url": product["url"],
          "price": product["price"],
          "in_stock": product["in_stock"]
        }

        print(data)

        batcher.product.upsert(
          where={
            "id": f"{site_name.value}_{product['sku'].replace(' ', '-').lower()}"
          },
          data={
            "create": data,
            "update": data
          }
        )

@router.get("/scraper/better", tags=["scraper"])
async def better_urls():
  result = BetterScraper.scrape_all()

  dump(result, open("better_all.json", "w"), indent=2)

  return result

@router.post("/scraper/better/csv", tags=["scraper"])
async def export_better_csv():
  BetterScraper.export_all_csv("data/better_all.csv")

  return FileResponse("data/better_all.csv")
