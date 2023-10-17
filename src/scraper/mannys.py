from httpx import AsyncClient
from json import dumps

from . import scrapers

class MannysScraper(scrapers.Scraper):
  id = "mannys"
  _base_url = "https://search.soundbay.com.au/multi_search"

  @classmethod
  async def search_query(cls, query: str, client: AsyncClient):
    page = 1

    while True:
      data = {
        "hits": 0,
        "products": []
      }

      params = {
        "searches": [
          {
            "q": query,
            "collection": "mproducts",
            "enable_overrides": True,
            "facet_by": "in_stock,brand,product_statuses,displayed_category,price",
            "filter_by": "",
            "highlight_full_fields": "title,sid",
            "max_facet_values": 100,
            "num_typos": 1,
            "page": page,
            "per_page": 250,
            "query_by": "title,description,sid",
            "query_by_weights": "10,1,1",
            "sort_by": "_text_match:desc,category_weight:desc,popularity:desc",
            "typo_tokens_threshold": 1
          }
        ]
      }

      cls.log().info(f"Scraping page {page}...")

      req = await client.post(
        cls._base_url,
        params={
          "x-typesense-api-key": "hwF2Qt89KwjgwvwjcNcB0ALMuKa2vvNJ"
        },
        data=dumps(params)
      )

      if req.status_code != 200:
        cls.log().warn(f"Request halted with status {req.status_code}")
        break

      result = req.json()
      result = result["results"][0]

      if len(result["hits"]) > 0:
        for res in result["hits"]:
          product = res["document"]

          data["products"].append({
            "name": product["title"],
            "sku": product["sid"][4:], # every mannys sku starts with XXX-
            "url": "https://www.mannys.com.au" + product["url"],
            "price": product["price"],
            "in_stock": product["stock"] == "in stock"
          })
      
      else:
        break

      data["hits"] = len(result["hits"])

      yield data
      
      page += 1
  
  @classmethod
  async def scrape_all(cls, client: AsyncClient):
    async for data in cls.search_query("*", client):
      yield data