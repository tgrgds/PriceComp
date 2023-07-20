import argparse
import asyncio

from src.api import scraper
from src.type import SiteName
from src.scraper import SCRAPERS
from src.prisma import prisma

parser = argparse.ArgumentParser()

parser.add_argument("scraper", type=SiteName)

args = parser.parse_args()

async def run():
    await prisma.connect()
    await scraper.chunk_scrape(SCRAPERS[args.scraper])

asyncio.run(run())
