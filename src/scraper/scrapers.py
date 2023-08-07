import csv
from json import dump, dumps
from urllib.parse import urlencode
from httpx import AsyncClient

from src.type import ScraperData
from src.util.brands import MUSIPOS_BRANDS

class Scraper:
  id = "base"

  @classmethod
  async def scrape_all(cls, client: AsyncClient) -> ScraperData:
    raise NotImplementedError

  @classmethod
  def export_all_json(cls, path: str) -> ScraperData:
    # this defeats the purpose of yielding all the results in the first place
    # TODO: fix this
    data = [[p for p in d["products"]] for d in cls.scrape_all()][0]

    with open(path, "w") as file:
      dump(data, file, indent=2)
      
      file.close()

    return data

  @classmethod
  def export_all_csv(cls, path: str):
    with open(path, "w", newline="") as csvfile:
      writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
      
      writer.writerow(["sku", "name", "url", "price", "in_stock"])

      for data in cls.scrape_all():
        rows = [[product["sku"],
            product["name"],
            product["url"],
            product["price"],
            product["in_stock"]] for product in data["products"]]

        writer.writerows(rows)
    
    return data

# Sites that use Algolia have a paticular technique
class AlgoliaScraper(Scraper):
  id = "base"
  # base_url: str
  # req_headers: obj
  # params: obj (not including query, page, hitsperpage)
  # index_name: str

  # this is implemented by deriving classes
  # to grab the specific product data from each website
  @classmethod
  def algolia_product_object(data):
    raise NotImplementedError

  @classmethod
  async def search_query(cls, query: str, client: AsyncClient, page_limit: int = 1000) -> ScraperData:
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
            "indexName": cls.index_name or None,
            "params": urlencode({
              "query": query,
              "page": str(page),
              "hitsPerPage": str(page_limit),
              **cls.params
            })
          }
        ]
      }

      req = await client.post(
        cls.base_url + "/1/indexes/*/queries",
        json=params,
        headers=cls.req_headers
      )

      if not req.status_code == 200:
        print(f"Request halted with status {req.status_code}")
        break

      result = req.json()

      if len(result["results"][0]["hits"]) > 0:
        for product in result["results"][0]["hits"]:
          try:
            data["products"].append(cls.algolia_product_object(product))
          except KeyError: # some products don't have SKUs
            pass

          product_count += 1

        page += 1

      else:
        break

    data["hits"] = product_count

    return data

  # despite getting all 17k "hits" using "*" as a query we can only retrieve data from the first 1000
  # so this splits the queries up into several searches using every brand in musipos
  @classmethod
  async def scrape_all(cls, client: AsyncClient):
    # collect list of skus already added to reduce overlap
    skus = []

    for brand in MUSIPOS_BRANDS:
      print(f"Requesting brand {brand}...")

      data = await cls.search_query(brand, client)

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
