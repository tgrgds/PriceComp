import requests
from json import dumps
from math import ceil

from src.scraper import Scraper

class HaworthScraper(Scraper):
  _base_url = "https://xf4jznzbcrkyscz86354vplw-fast.searchtap.net/v2"

  @classmethod
  def search_query(cls, query: str):
    page = 0

    total_hits = 0

    while True:
      data = {
        "hits": 0,
        "products": []
      }

      params = {
        "count": 250,
        "query": query,
        "skip": 250 * page,
        "collection": "9L5M8FQRTBHCPWU4PU4I2VII",
        "facetCount": 100,
        "fields": ["*"],
        "filter": "priorityScore >= 0 AND publishedTimestamp < 1677022946276 AND publishedTimestamp > 0",
        "geo": {},
        "groupCount": -1,
        "highlightFields": [],
        "numericFacetFilters": { "price": ["[0,2147483647]"] },
        "searchFields": ["title", "description", "collections", "tags", "productType", "vendor", "variants.sku"],
      }

      print(f"Getting page {page}/{ceil(total_hits / 250)}...")

      req = requests.post(
        cls._base_url,
        headers={
          "authorization": "Bearer MEEDXH2Q5KN91ADWFHY7CF97",
          "Content-Type": "application/json"
        },
        data=dumps(params)
      )

      if not req.ok:
        print(f"Request halted with status {req.status_code}")

      results = req.json()
      total_hits = results["totalHits"]
      results = results["results"]
      hits = len(results)

      if hits > 0:
        for product in results:
          data["products"].append({
            "name": product["title"],
            "sku": product["variants"][0]["sku"],
            "url": "https://www.haworthguitars.com.au/products/" + product["handle"],
            "price": product["price"],
            "in_stock": product["in_stock"] == 1
          })

      else:
        break

      page += 1
      
      data["hits"] = hits

      yield data


  @classmethod
  def scrape_all(cls):
    for data in cls.search_query("*"):
      yield data