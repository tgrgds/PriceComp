import requests
from math import ceil

from . import scrapers

class DerringersScraper(scrapers.Scraper):
  id = "derringers"
  _base_url = "https://aucs31.ksearchnet.com/cs/v2/search"

  @classmethod
  def search_query(cls, query: str):
    page = 1

    total_hits = 0

    while True:
      data = {
        "hits": 0,
        "products": []
      }

      params = {
        "context":{
          "apiKeys":[
            "klevu-167634718759716056"
          ]
        },
        "recordQueries":[
          {
            "id":"productList",
            "typeOfRequest":"SEARCH",
            "settings":{
              "query":{
                "term":"*"
              },
              "typeOfRecords":[
                "KLEVU_PRODUCT"
              ],
              "limit":"100",
              "offset": str(100 * page),
              "searchPrefs":[
                "searchCompoundsAsAndQuery"
              ],
              "fallbackQueryId":"productListFallback"
            }
          }
        ]
      }

      print(f"Getting page {page}/{ceil(total_hits / 100)}...")

      req = requests.post(
        cls._base_url,
        json=params
      )

      if not req.ok:
        print(f"Request halted with status {req.status_code}")

      results = req.json()["queryResults"][0]
      total_hits = results["meta"]["totalResultsFound"]
      results = results["records"]
      hits = len(results)

      if hits > 0:
        for product in results:
          if (product["sku"] == None): continue
          data["products"].append({
            "name": product["name"],
            # skus have a BRAND_ prefix with max 4 letters but sometimes shorter (i.e. AKG)
            "sku": product["sku"][product["sku"].find("_") + 1:],
            "url": product["url"],
            "price": float(product["salePrice"]),
            "in_stock": product["inStock"] == "yes"
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