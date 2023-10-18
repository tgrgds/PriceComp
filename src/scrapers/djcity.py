from urllib.parse import urlencode
import logging

from . import scraper

class DjcityScraper(scraper.AlgoliaScraper):
  id = "djcity"
  base_url = "https://i2uwp1cwqx-dsn.algolia.net"
  req_headers = {
    "x-algolia-api-key": "b04ee3475d7cf8570c233690b0ba8326",
    "x-algolia-application-id": "I2UWP1CWQX",
    "content-type": "application/x-www-form-urlencoded",
    # "x-algolia-agent": "Algolia for JavaScript (4.13.0); Browser"
  }
  index_name = "prod_products"
  params = {
    "userToken": "anonymous-824045a6-72e2-4d70-b7a6-fe2c0f54e1a3"
  }

  @classmethod
  def algolia_product_object(cls, data):
    return {
      "name": data["title"],
      "sku": str(data["sku"]),
      "url": data["url"],
      "price": data["price"],
      "in_stock": data["inStock"],
    }
