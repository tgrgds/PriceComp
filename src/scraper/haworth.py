import requests
from json import dumps
from math import ceil

from . import scraper

class HaworthScraper(scraper.Scraper):
  id = "haworth"
  _base_url = "https://svc-5-usf.hotyon.com/instantsearch"

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
        "q": "",
        "apiKey": "3877fc75-49a9-44e4-9394-12e6916904a7",
        "sort": "bestselling",
        "take": 250,
        "country": "AU",
        "locale": "en",
        "skip": 250 * page,
        # "count": 250,
        # "query": query,
        # "collection": "9L5M8FQRTBHCPWU4PU4I2VII",
        # "facetCount": 100,
        # "fields": ["*"],
        # "filter": "priorityScore >= 0 AND publishedTimestamp < 1677022946276 AND publishedTimestamp > 0",
        # "geo": {},
        # "groupCount": -1,
        # "highlightFields": [],
        # "numericFacetFilters": { "price": ["[0,2147483647]"] },
        # "searchFields": ["title", "description", "collections", "tags", "productType", "vendor", "variants.sku"],
      }

      # ?q=&apiKey=3877fc75-49a9-44e4-9394-12e6916904a7&sort=bestselling&take=6&country=AU&locale=en

      print(f"Getting page {page}/{ceil(total_hits / 250)}...")

      req = requests.post(
        cls._base_url,
        # headers={
        #   "authorization": "Bearer MEEDXH2Q5KN91ADWFHY7CF97",
        #   "Content-Type": "application/json"
        # },
        params=params
      )

      if not req.ok:
        print(f"Request halted with status {req.status_code}")

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
  def scrape_all(cls):
    for data in cls.search_query("*"):
      yield data