import requests
from math import ceil
from urllib.parse import urlencode

from . import scrapers

class SkyScraper(scrapers.Scraper):
  id = "sky"
  _base_url = "https://skymusic.com.au"

  @classmethod
  def search_query(cls, query: str):
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

      print(f"Getting page {page}/{ceil(total_hits / 24)}...")

      req = requests.get(
        "https://services.mybcapps.com/bc-sf-filter/search",
        params=params
      )

      if not req.ok:
        print(f"Request failed with status {req.status_code}")
        continue

      results = req.json()
      total_hits = results["total_product"]

      # get and compare product list hashes
      product_hash = hash(str(results["products"]))
      if product_hash == last_page_hash:
        print("Got duplicate page. This should mean we're done.")
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

      print(data["hits"])

      page += 1

      yield data
  
  @classmethod
  def scrape_all(cls):
    for data in cls.search_query("*"):
      yield data
