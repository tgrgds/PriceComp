from urllib.parse import urlencode

from . import scrapers

class BetterScraper(scrapers.AlgoliaScraper):
  id = "better"
  base_url = "https://g6qbk0086l-dsn.algolia.net"
  req_headers = {
    "x-algolia-api-key": "MGE2NjEzZjlmNGE4ZTEwMTQyMjc1MGRhNzkwMTcxOTU1ZDllOTcyNDllMWNjZTkxZjE0YmJkN2ZmYjM0ODMxNHRhZ0ZpbHRlcnM9",
    "x-algolia-application-id": "G6QBK0086L",
    "content-type": "application/x-www-form-urlencoded"
  }
  index_name = "bm_prod_default_products"
  params = {
    "ruleContexts": '["magento_filters"]',
    "facets": '["in_stock","magefan_blog_post","manufacturer","colorfilter","price.AUD.default"]'
  }

  @classmethod
  def algolia_product_object(cls, data):
    return {
      "name": data["name"],
      "sku": str(data["musipos"]),
      "url": data["url"],
      "price": data["price"]["AUD"]["default"],
      "in_stock": data["in_stock"] == "In stock", # better says "Order" if not in stock
    }
