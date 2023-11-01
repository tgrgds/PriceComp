from asyncio import sleep
from math import floor
from httpx import AsyncClient
from bs4 import BeautifulSoup

from src.type import ScraperData
from . import scraper

class SoundsEasyScraper(scraper.Scraper):
  id = "soundseasy"
  _base_url = "https://www.soundseasy.com.au/search"
  _last_wait = 5

  @classmethod
  def wait(cls):
    cls.log().info(f"Got error 430, sleeping for {cls._last_wait} seconds...")
    sleep(cls._last_wait)

    cls._last_wait += 5

  @classmethod
  async def search_query(cls, query: str, client: AsyncClient):
    page = 1

    total_hits = 0

    while True:
      data = {
        "hits": 0,
        "products": []
      }

      params = {
        "type": "product",
        "q": query,
        "page": page
        # "view": "json",
      }

      cls.log().info(f"Getting page {page}/{floor(total_hits / 250)}...")

      req = await client.get(
        cls._base_url,
        params=params,
        headers={
          "Proxy-Authorization": "Basic MTQzZGk2b29kNWk2aWJhOjA0WjRCM2g4T2VNRGpKTQ=="
        }
      )

      if req.status_code != 200:
        cls.log().warn(f"Page request halted with status {req.status_code}")
        if req.status_code == 430:
          cls.wait()
          continue

      soup = BeautifulSoup(req.text, "html.parser")

      if not soup.find("a", { "class": "boost-pfs-filter-product-item-title" }): break

      # we're just looking at each search result, visiting the page and getting some details
      # this occasionally causes a 430 (shopify's version of 429) so it takes a while to go through everything
      for card in soup.find_all("a", { "class": "boost-pfs-filter-product-item-title" }):
        p = await client.get("https://www.soundseasy.com.au" + card["href"])
        ps = BeautifulSoup(p.text, "html.parser")

        if p.status_code != 200:
          cls.log().warn(f"Product request halted with status {p.status_code}")
          if p.status_code == 430:
            cls.wait()

        try:
          sku = ps.find("p", { "class": "sku" }).text

          data["products"].append({
            "sku": sku[sku.find("-") + 1:].strip(),
            "name": ps.find("h1", { "class": "product_name" }).text.strip(),
            "price": float(ps.find("span", { "class": "current_price" }).text[2:].strip().replace(",", "")),
            "url": "https://soundseasy.com.au" + card["href"],
            "in_stock": ps.find("div", { "class": "items_left" }) != None
          })

        except Exception as e:
          cls.log().info(f"Skipping due to error: {e}")
          pass

      yield ScraperData(products=data["products"], progress=page/floor(total_hits / 250))

      page += 1


  @classmethod
  async def scrape_all(cls, client: AsyncClient) -> ScraperData:
    async for data in cls.search_query("*", client):
      yield data