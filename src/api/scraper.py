from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends

from src.prisma import prisma
from src.auth import api_key_auth
from src.scraper import Scraper
from src.scraper.better import BetterScraper
from src.scraper.mannys import MannysScraper
from src.scraper.haworth import HaworthScraper
from src.type import SiteName

router = APIRouter()

# site_id's go here to keep track of background tasks
# so we don't double up on scrapers
scraper_queue = []

async def chunk_scrape(scraper: Scraper):
  for chunk in scraper.scrape_all():
    async with prisma.batch_() as batcher:
      for product in chunk["products"]:
        data = {
          "id": f"{scraper.id}_{product['sku'].replace(' ', '-').lower()}",
          "store_id": scraper.id,
          "sku": product["sku"],
          "url": product["url"],
          "price": product["price"],
          "in_stock": product["in_stock"]
        }

        print(data)

        batcher.product.upsert(
          where={
            "id": f"{scraper.id}_{product['sku'].replace(' ', '-').lower()}"
          },
          data={
            "create": data,
            "update": data
          }
        )
  
  scraper_queue.remove(scraper.id)

@router.post("/scraper/{site_name}", status_code=201, dependencies=[Depends(api_key_auth)],
             tags=["scraper"], description="Get all data from a competitor site and update the database.")
async def scrape_site(site_name: SiteName, background_tasks: BackgroundTasks):
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

  if (site_name not in scraper_queue):
    # TODO: exception handling
    background_tasks.add_task(chunk_scrape, scraper)
    scraper_queue.append(site_name)
  
  else:
    raise HTTPException(status_code=400, detail="Scraper already running.")

  return { "message": "Background task scheduled" }
