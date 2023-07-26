import requests
from json import dumps, loads
from time import sleep
from math import ceil
from bs4 import BeautifulSoup

from . import scrapers

class SoundsEasyScraper(scrapers.Scraper):
  id = "soundseasy"
  _base_url = "https://www.soundseasy.com.au/search"
  _last_wait = 5

  @classmethod
  def wait(cls):
    print(f"Got error 430, sleeping for {cls._last_wait} seconds...")
    sleep(cls._last_wait)

    cls._last_wait += 5

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
        "type": "product",
        "q": query,
        "page": page
        # "view": "json",
      }

      print(f"Getting page {page}/{ceil(total_hits / 250)}...")

      req = requests.get(
        cls._base_url,
        params=params,
        headers={
          "Proxy-Authorization": "Basic MTQzZGk2b29kNWk2aWJhOjA0WjRCM2g4T2VNRGpKTQ=="
        }
      )

      if not req.ok:
        print(f"Request halted with status {req.status_code}")
        if req.status_code == 430:
          cls.wait()
          continue

      soup = BeautifulSoup(req.text, "html.parser")

      if not soup.find("a", { "class": "boost-pfs-filter-product-item-title" }): break

      # we're just looking at each search result, visiting the page and getting some details
      # this occasionally causes a 430 (shopify's version of 429) so it takes a while to go through everything
      for card in soup.find_all("a", { "class": "boost-pfs-filter-product-item-title" }):
        p = requests.get("https://soundseasy.com.au" + card["href"])
        ps = BeautifulSoup(p.text, "html.parser")

        if not p.ok:
          print(f"Request halted with status {p.status_code}")
          if p.status_code == 430:
            cls.wait()

        try:
          sku = ps.find("p", { "class": "sku" }).text

          data["products"].append({
            "sku": sku[sku.find("-") + 1:].strip(),
            "name": ps.find("h1", { "class": "product_name" }).text.strip(),
            "price": float(ps.find("span", { "class": "current_price" }).text[2:].strip().replace(",", "")),
            "url": "https://soundseasy.com.au" + card["href"],
            "in_stock": ps.find("div", { "class": "items_left" }) != None
          })

          print(sku)
        except Exception as e:
          print(f"Skipping due to error: {e}")
          pass

      # for product in results["results"]:
      #   data["products"].append({
      #     "name": product["title"],
      #     # "sku": 
      #     "url": "https://soundseasy.com.au" + product["url"],
      #     "price": int(product["raw_price"]) / 100
      #   })

      yield data

      page += 1


  @classmethod
  def scrape_all(cls):
    for data in cls.search_query("*"):
      yield data