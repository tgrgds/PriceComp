from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from prisma.errors import FieldNotFoundError
from datetime import datetime
from time import time
import httpx
import logging
import re

from src.prisma import prisma
from src.auth import api_key_auth
from src.scrapers import Scraper, SCRAPERS
from src.type import SiteName, ScraperData

router = APIRouter()

# site_id's go here to keep track of background tasks
# so we don't double up on scrapers
scraper_queue = []

async def chunk_scrape(scraper: Scraper):
  logger = logging.getLogger(scraper.id)
  batch_count = 0
  error_count = 0
  failed = False
  progress = 0

  _starttime = time()

  async with httpx.AsyncClient() as client:
    try:
      chunk: ScraperData
      async for chunk in scraper.scrape_all(client):
        batch_count += 1

        progress = chunk.progress

        # TODO: consider adding a timeout (5-10 minutes or something)
        # So far all scrapers that end up idling have been because of uncaught and silent exceptions
        # (which now get caught and logged below)
        # so might not be a need for now.

        try:
          async with prisma.batch_() as batcher:
            for product in chunk.products:
              data = {
                "id": f"{scraper.id}_{product.sku.replace(' ', '-').lower()}",
                "store_id": scraper.id,
                "sku": product.sku,
                "sku_trunc": re.sub(r'[^a-zA-Z0-9]', '', product.sku),
                "url": product.url,
                "price": float(product.price),
                "in_stock": product.in_stock
              }

              logger.debug(data)

              batcher.product.upsert(
                where={
                  "id": f"{scraper.id}_{product.sku.replace(' ', '-').lower()}"
                },
                data={
                  "create": data,
                  "update": data
                }
              )
        # Exception when submitting batch to prisma
        except Exception as e:
          logger.error(f"Batch failed!")
          logger.exception(e)
          error_count += 1
    
    # Exception when scraping batch
    except Exception as e:
      logger.error("Scraper failed due to uncaught exception!")
      logger.exception(e)
      failed = True

    if error_count > 0:
      logger.warn(f"{error_count} out of {batch_count} batches failed!")

    try:
      scraper_queue.remove(scraper.id)
    except:
      pass

  # Update competitor status data
  await prisma.competitor.update(
    where={ "store_id": scraper.id },
    data={
      "last_scrape": datetime.now(),
      "last_scrape_duration": time() - _starttime,
      "last_scrape_failed": failed,
      "last_scrape_progress": float(progress)
    }
  )

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

# Get the status of all scrapers
# Including product count and any other useful info
@router.get("/scraper/status", dependencies=[Depends(api_key_auth)])
async def scraper_status():
  data = []

  for site in SiteName:
    product_count = await prisma.product.count(where={
      "store_id": site.value
    })

    comp = await prisma.competitor.find_first(where={ "store_id": site.value })

    # TODO: last scrape duration, last scrape datetime
    data.append({
      "store_id": site.value,
      "product_count": product_count,
      "running": site.value in scraper_queue,
      "last_scrape": {
        "date": comp.last_scrape,
        "duration": comp.last_scrape_duration,
        "failed": comp.last_scrape_failed,
        "progress": comp.last_scrape_progress
      } if comp.last_scrape else None,
    })
  
  return data
