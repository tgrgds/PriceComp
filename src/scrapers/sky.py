from httpx import AsyncClient
from math import floor
from urllib.parse import urlencode

from src.type import ScraperData
from . import scraper

class SkyScraper(scraper.Scraper):
  id = "sky"
  _base_url = "https://skymusic.com.au"

  @classmethod
  async def search_query(cls, query: str, client: AsyncClient):
    data = {
      "hits": 0,
      "products": []
    }

    page = 1
    total_hits = 0

    # for some reason when we surpass the last page
    # it keeps returning the same page over and over again
    # so we record a quick hash of the products table
    # and terminate when its identical to the current products
    last_page_hash = ""

    while True:

      params = urlencode({
        "q": query,
        "page": page,
        "type": "product",
        "shop": "sky-music-australia.myshopify.com",
        "limit": "24", # values higher than 24 just give us 20 products
      })

      cls.log().info(f"Getting page {page}/{floor(total_hits / 24)}...")

      req = await client.get(
        "https://services.mybcapps.com/bc-sf-filter/search",
        params=params
      )

      if req.status_code != 200:
        cls.log().warn(f"Request failed with status {req.status_code}")
        continue

      results = req.json()
      total_hits = results["total_product"]

      # get and compare product list hashes
      product_hash = hash(str(results["products"]))
      if product_hash == last_page_hash:
        cls.log().info("Got duplicate page. This should mean we're done.")
        break
      else: last_page_hash = product_hash

      data["hits"] = len(results["products"])

      for product in results["products"]:
        if not product["variants"][0]["sku"]: continue

        data["products"].append({
          "name": product["title"],
          "sku": product["variants"][0]["sku"],
          "price": float(product["variants"][0]["price"]),
          "url": cls._base_url + "/collections/all/products/" + product["handle"],
          "in_stock": product["available"]
        })

      page += 1

      yield ScraperData(products=data["products"], progress=page/floor(total_hits / 24))
  
  @classmethod
  async def scrape_all(cls, client: AsyncClient) -> ScraperData:
    async for data in cls.search_query("*", client):
      yield data
