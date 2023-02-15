from fastapi import APIRouter
from fastapi.responses import FileResponse
from json import dump

from src.scraper.better import BetterScraper

router = APIRouter()

@router.get("/scraper/better", tags=["scraper"])
async def better_urls():
  result = BetterScraper.scrape_all()

  dump(result, open("better_all.json", "w"), indent=2)

  return result

@router.post("/scraper/better/csv", tags=["scraper"])
async def export_better_csv():
  BetterScraper.export_all_csv("data/better_all.csv")

  return FileResponse("data/better_all.csv")
