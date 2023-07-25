import requests
from json import dumps
from urllib.parse import urlencode

from . import scraper
from src.type import ScraperData
from src.util.brands import MUSIPOS_BRANDS

# curl 'https://qzcseio8f2-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%3B%20Magento2%20integration%20(3.2.0)%3B%20autocomplete.js%200.38.0&x-algolia-application-id=QZCSEIO8F2&x-algolia-api-key=ZmI2NDhlZDY3MDE1NTM4Mzg2MTNmYTZmNmNhZDQ0MzQxOTQxNjQ3YzY3Mjg3NzczNTVlNmIyY2Y2ZGUzYmQzNXRhZ0ZpbHRlcnM9' --compressed -X POST -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0' -H 'Accept: application/json' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' -H 'content-type: application/x-www-form-urlencoded' -H 'Origin: https://www.turramusic.com.au' -H 'Connection: keep-alive' -H 'Referer: https://www.turramusic.com.au/' -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: cross-site' --data-raw '{"requests":[{"indexName":"live_default_categories","params":"query=*&hitsPerPage=2&analyticsTags=autocomplete&clickAnalytics=true&numericFilters=include_in_menu%3D1"},{"indexName":"live_default_products","params":"query=*&hitsPerPage=6&analyticsTags=autocomplete&clickAnalytics=true&facets=%5B%22categories.level0%22%5D&numericFilters=visibility_search%3D1&ruleContexts=%5B%22magento_filters%22%2C%22%22%5D"}]}'

class TurraScraper(scraper.Scraper):
  id = "turra"
  _base_url = "https://qzcseio8f2-dsn.algolia.net"
  _req_headers = {
      "x-algolia-agent": "Algolia for JavaScript (3.35.1); Browser; Magento2 integration (3.2.0); autocomplete.js 0.38.0",
      "x-algolia-application-id": "QZCSEIO8F2",
      "x-algolia-api-key": "ZmI2NDhlZDY3MDE1NTM4Mzg2MTNmYTZmNmNhZDQ0MzQxOTQxNjQ3YzY3Mjg3NzczNTVlNmIyY2Y2ZGUzYmQzNXRhZ0ZpbHRlcnM9"
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
            "indexName": "live_default_products",
            "params": urlencode({
              "query": query,
              "page": str(page),
              "hitsPerPage": str(page_limit),
              "ruleContexts": '["magento_filters"]',
              "facets": '["categories.level0"]'
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
              # turra skus:
              #   1. are random ass numbers with no relation to normal skus
              #   2. arent even in this payload >:(
              "sku": str(product["objectID"]),
              "url": product["url"],
              "price": product["price"]["AUD"]["default"],
              "in_stock": False, # also no instock value that i can grab
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