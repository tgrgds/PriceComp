import requests
from json import dumps
from urllib.parse import urlencode

from src.scraper import Scraper
from src.type import ScraperData
from src.util.brands import MUSIPOS_BRANDS

class BetterScraper(Scraper):
  id = "better"
  _base_url = "https://g6qbk0086l-dsn.algolia.net"
  _req_headers = {
    "x-algolia-api-key": "MGE2NjEzZjlmNGE4ZTEwMTQyMjc1MGRhNzkwMTcxOTU1ZDllOTcyNDllMWNjZTkxZjE0YmJkN2ZmYjM0ODMxNHRhZ0ZpbHRlcnM9",
    "x-algolia-application-id": "G6QBK0086L",
    "content-type": "application/x-www-form-urlencoded"
  }

  @classmethod
  def search_request(cls, query: str, page_limit: int = 1000) -> ScraperData:
    data = {
      "hits": 0,
      "products": []
    }

    # TODO: consider using algolia cursor instead of pagination
    # see https://www.algolia.com/doc/rest-api/search/#pagination
    page = 0
    product_count = 0

    while True:
      params = {
        "requests": [
          {
            "indexName": "bm_prod_default_products",
            "params": urlencode({
              "query": query,
              "page": str(page),
              "hitsPerPage": str(page_limit),
              "ruleContexts": '["magento_filters"]',
              "facets": '["in_stock","magefan_blog_post","manufacturer","colorfilter","price.AUD.default"]'
            }),
          }
        ]
      }

      req = requests.post(
        cls._base_url + "/1/indexes/*/queries",
        data=dumps(params),
        headers=cls._req_headers
      )

      if not req.ok:
        print(f"Request halted with status {req.status_code}")
        break

      result = req.json()

      if len(result["results"][0]["hits"]) > 0:
        for product in result["results"][0]["hits"]:
          try:
            data["products"].append({
              "name": product["name"],
              "sku": str(product["musipos"]),
              "url": product["url"],
              "price": product["price"]["AUD"]["default"],
              "in_stock": product["in_stock"] == "In stock", # better says "Order" if not in stock
            })
          except KeyError: # some products don't have SKUs
            pass

          product_count += 1

        page += 1

      else:
        #print("Finished scraping!")
        break

    data["hits"] = product_count

    return data

  # despite getting all 17k "hits" using "*" as a query we can only retrieve data from the first 1000
  # so this splits the queries up into several searches using every brand in musipos
  @classmethod
  def scrape_all(cls):
    # collect list of skus already added to reduce overlap
    # with overlap we get 104877 results :O
    skus = []

    for brand in MUSIPOS_BRANDS:
      print(f"Requesting brand {brand}...")

      data = cls.search_request(brand)

      products = []

      # get rid of the duplicate skus
      for prod in filter(lambda p: p["sku"] not in skus, data["products"]):
        products.append(prod)

      new_hits = len(products)

      print(f"{data['hits']} hits - {data['hits'] - new_hits} duplicates = {new_hits} products added")

      # skip if no products to add
      if new_hits == 0:
        continue

      # add to the list of SKUs that have been put into the results
      # so we don't get duplicates
      skus += [p["sku"] for p in products if p["sku"] not in skus]

      yield {
        "hits": new_hits,
        "products": products
      }

    #return data