from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from prisma.errors import FieldNotFoundError
import httpx
import logging
import re

from src.prisma import prisma
from src.auth import api_key_auth
from src.scrapers import Scraper, SCRAPERS
from src.type import SiteName

router = APIRouter()

# site_id's go here to keep track of background tasks
# so we don't double up on scrapers
scraper_queue = []

async def chunk_scrape(scraper: Scraper):
  logger = logging.getLogger(scraper.id)
  batch_count = 0
  error_count = 0

  async with httpx.AsyncClient() as client:
    async for chunk in scraper.scrape_all(client):
      batch_count += 1

      try:
        async with prisma.batch_() as batcher:
          for product in chunk["products"]:
            data = {
              "id": f"{scraper.id}_{product['sku'].replace(' ', '-').lower()}",
              "store_id": scraper.id,
              "sku": product["sku"],
              "sku_trunc": re.sub(r'[^a-zA-Z0-9]', '', product["sku"]),
              "url": product["url"],
              "price": float(product["price"]),
              "in_stock": product["in_stock"]
            }

            logger.debug(data)

            batcher.product.upsert(
              where={
                "id": f"{scraper.id}_{product['sku'].replace(' ', '-').lower()}"
              },
              data={
                "create": data,
                "update": data
              }
            )
      except Exception as e:
        logger.error("Batch failed!")
        logger.error(e)
        error_count += 1

    if error_count > 0:
      logger.warn(f"{error_count} out of {batch_count} batches failed!")

    try:
      scraper_queue.remove(scraper.id)
    except:
      pass

@router.post("/scraper/{site_name}", status_code=201, dependencies=[Depends(api_key_auth)],
             tags=["scraper"], description="Get all data from a competitor site and update the database.")
async def scrape_site(site_name: SiteName, background_tasks: BackgroundTasks):
  
  try:
    scraper = SCRAPERS[site_name]
  except KeyError:
    raise HTTPException(status_code=400, detail="The requested site does not exist.")

  if (site_name not in scraper_queue):
    # TODO: exception handling
    background_tasks.add_task(chunk_scrape, scraper)
    scraper_queue.append(site_name)
  
  else:
    raise HTTPException(status_code=400, detail="Scraper already running.")

  return { "message": "Background task scheduled" }

# List all available sites
# Saves having to update a sitelist in cronjob lol
@router.get("/scraper/list", dependencies=[Depends(api_key_auth)])
async def list_sites():
  sites = [site.value for site in SiteName]

  return sites
