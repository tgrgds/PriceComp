from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from json import dump

from src.prisma import prisma
from src.scraper import Scraper
from src.scraper.better import BetterScraper
from src.scraper.mannys import MannysScraper
from src.scraper.haworth import HaworthScraper
from src.type import SiteName

router = APIRouter()

@router.post("/scraper/{site_name}", tags=["scraper"], description="Get all data from a competitor site and update the database.")
async def scrape_site(site_name: SiteName):
  scraper: Scraper = None

  # todo: make this better when more scrapers come in
  if site_name == SiteName.better:
    scraper = BetterScraper

  elif site_name == SiteName.mannys:
    scraper = MannysScraper

  elif site_name == SiteName.haworth:
    scraper = HaworthScraper

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