from math import floor
from httpx import AsyncClient
from bs4 import BeautifulSoup

from src.type import ScraperData
from . import scraper

class MegaScraper(scraper.Scraper):
  id = "mega"
  _base_url = "https://www.megamusiconline.com.au"

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
        "s": "",
        "post_type": "product"
      }

      cls.log().info(f"Getting page {page}/{floor(total_hits / 32)}...")

      req = await client.get(cls._base_url + f"/page/{page}", params=params, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
      })

      if req.status_code == 404:
        cls.log().info("Pagelist exhausted!")
        break
      elif req.status_code != 200:
        cls.log().warn(f"Page request halted with status {req.status_code}")
        break

      soup = BeautifulSoup(req.text, "html.parser")

      # Example of woocommerce-result-count text: "Showing 1&ndash;32 of 24187 results"
      _rcount = soup.find("p", { "class": "woocommerce-result-count" }).text.strip()
      total_hits = int(_rcount[_rcount.find("of ")+ 3:_rcount.rfind(" ")])

      for card in soup.find_all("div", { "class": "type-product" }):
        product = card.find("span", { "class": "gtm4wp_productdata" })

        stock = product.get("data-gtm4wp_product_stocklevel")

        data["products"].append({
          "sku": card.find("a", { "class": "button" }).get("data-product_sku"),
          "name": product.get("data-gtm4wp_product_name"),
          "price": product.get("data-gtm4wp_product_price"),
          "url": product.get("data-gtm4wp_product_url"),
          "in_stock": int(stock) > 0 if stock else False
        })

      page += 1

      yield ScraperData(products=data["products"], progress=page/floor(total_hits / 32))

  @classmethod
  async def scrape_all(cls, client: AsyncClient) -> ScraperData:
    async for data in cls.search_query("*", client):
      yield data
