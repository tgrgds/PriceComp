from httpx import AsyncClient, get
from math import floor
from bs4 import BeautifulSoup
# from concurrent.futures import ThreadPoolExecutor
# import asyncio

from src.type import ScraperData
from . import scraper

# TODO: this shit takes FOREVER (several hours) to scrape everything
# This def needs to be faster

# makes request to /V1/search and gets the total_count value from here
# to be able to accurately measure progress during the scrape
async def get_total_hits():
  req = get(
    "https://billyhydemusic.com.au/rest/default/V1/search?searchCriteria%5BrequestName%5D=catalog_view_container&searchCriteria%5BfilterGroups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bfield%5D=price.from&searchCriteria%5BfilterGroups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bvalue%5D=0&searchCriteria%5BfilterGroups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bfield%5D=price.to&searchCriteria%5BfilterGroups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bvalue%5D=100000"
  )

  data = req.json()

  return int(data["total_count"])

class BillyHydeScraper(scraper.Scraper):
  id = "billyhyde"
  _base_url = "https://billyhydemusic.com.au/"

  @classmethod
  async def fetch_product_details(cls, client: AsyncClient, product):
    try:
      price = product["price_info"]["final_price"]
      name = product["name"]
      url = product["url"]

      p = await client.get(url)

      if p.status_code != 200:
        cls.log().warn(f"Couldn't get page for {name}! (Code {p.status_code})")
        return None

      soup = BeautifulSoup(p.text, "html.parser")

      sku = soup.find("div", { "class": "product_sku" }).text.strip()[5:]
      in_stock = not not soup.find("span", { "class": "stock yes" })

      return {
        "name": name,
        "sku": sku,
        "url": url,
        "price": price,
        "in_stock": in_stock
      }
    except:
      cls.log().warn(f"Got exception!")
      # cls.log().exception(e)


  @classmethod
  async def scrape_all(cls, client: AsyncClient) -> ScraperData:
    page = 1
    page_size = 50

    cls.log().info("Getting total_count...")
    total_hits = await get_total_hits()
    cls.log().info(f"There are {total_hits} total products")

    while True:
      data = {
        "hits": 0,
        "products": []
      }

      params = {
        # a page of 200 products is ~1mb response size
        "searchCriteria[pageSize]": page_size,
        "searchCriteria[currentPage]": page,
        "storeId": 1,
        "currencyCode": "AUD"
      }

      cls.log().info(f"Getting page {page}/{floor(total_hits / page_size)}...")
      
      req = await client.get(
        cls._base_url + "rest/V1/products-render-info/",
        params=params
      )

      if req.status_code != 200:
        cls.log().warn(f"Request halted with status {req.status_code}")

      req = req.json()
      
      # TODO: find a way to do concurrent requests
      # using a threadpoolexecutor like this ends up sending requests
      # at the same speed as just doing it sequentially
      # the only difference is that if the batch size is too big
      # most of them give a 503 error

      # with ThreadPoolExecutor(max_workers=5) as executor:
        # product_tasks = []

      for k, product in enumerate(req["items"]):

        cls.log().info(f"({k + 1}/{page_size}) {product['name']}")

        p = await cls.fetch_product_details(client, product) #asyncio.to_thread(cls.fetch_product_details, client, product)
        if p:
          data["products"].append(p)
          # product_tasks.append(task)

        # product_results = await asyncio.gather(*product_tasks)

        # data["products"] = [p for p in product_results if p]
        # cls.log().info(f"{len(data['products'])}/{page_size} products captured.")

      
      yield ScraperData(products=data["products"], progress=page/floor(total_hits / page_size))

      page += 1

      