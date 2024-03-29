from httpx import AsyncClient
from math import floor

from src.type import ScraperData
from . import scraper

class DerringersScraper(scraper.Scraper):
  id = "derringers"
  _base_url = "https://aucs31.ksearchnet.com/cs/v2/search"

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
                "term": query
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

      cls.log().info(f"Getting page {page}/{floor(total_hits / 100)}...")

      req = await client.post(
        cls._base_url,
        json=params
      )

      if req.status_code != 200:
        cls.log().warn(f"Request halted with status {req.status_code}")

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

      data["hits"] = hits

      yield ScraperData(products=data["products"], progress=page/floor(total_hits / 100))

      page += 1

  @classmethod
  async def scrape_all(cls, client: AsyncClient) -> ScraperData:
    async for data in cls.search_query("*", client):
      yield data