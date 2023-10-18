from httpx import AsyncClient
from math import ceil

from . import scraper

class HaworthScraper(scraper.Scraper):
  id = "haworth"
  _base_url = "https://svc-5-usf.hotyon.com/instantsearch"

  @classmethod
  async def search_query(cls, query: str, client: AsyncClient):
    page = 0

    total_hits = 0

    while True:
      data = {
        "hits": 0,
        "products": []
      }

      params = {
        "q": query,
        "apiKey": "3877fc75-49a9-44e4-9394-12e6916904a7",
        "sort": "bestselling",
        "take": 250,
        "country": "AU",
        "locale": "en",
        "skip": 250 * page,
      }

      cls.log().info(f"Getting page {page}/{ceil(total_hits / 250)}...")

      req = await client.post(
        cls._base_url,
        params=params
      )

      if not req.status_code == 200:
        cls.log().warn(f"Request halted with status {req.status_code}")

      results = req.json()["data"]
      total_hits = results["total"]
      results = results["items"]
      hits = len(results)

      if hits > 0:
        for product in results:
          if (product["variants"][0]["sku"] == None): continue
          data["products"].append({
            "name": product["title"],
            "sku": product["variants"][0]["sku"],
            "url": "https://www.haworthguitars.com.au/products/" + product["urlName"],
            "price": product["variants"][0]["price"],
            "in_stock": product["variants"][0]["available"] == 1
          })

      else:
        break

      page += 1
      
      data["hits"] = hits

      yield data

  @classmethod
  async def scrape_all(cls, client: AsyncClient):
    async for data in cls.search_query("", client):
      yield data