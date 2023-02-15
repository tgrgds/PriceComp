import requests
from json import dumps
from urllib.parse import urlencode

from src.scraper.scraper import Scraper
from src.util.brands import MUSIPOS_BRANDS

class MannysScraper(Scraper):
  _base_url = "https://search.soundbay.com.au/multi_search"

  @classmethod
  def search_query(cls, query: str):
    data = {
      "totalHits": 0,
      "hits": 0,
      "products": []
    }

    page = 1
    product_count = 0

    while True:
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

      print(f"Scraping page {page}...")

      req = requests.post(
        cls._base_url,
        params={
        "x-typesense-api-key": "hwF2Qt89KwjgwvwjcNcB0ALMuKa2vvNJ"
        },
        data=dumps(params)
      )

      if not req.ok:
        print(f"Request halted with status {req.status_code}")
        break

      # dump(req.json(), open("data/mannys.json", "w"), indent=2)

      result = req.json()
      result = result["results"][0]
      print(len(result["hits"]))

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

          # this could just be len(data["products"]) instead lol
          product_count += 1
      
      else:
        break
      
      page += 1

    data["hits"] = product_count

    return data
  
  @classmethod
  def scrape_all(cls):
    return cls.search_query("*")