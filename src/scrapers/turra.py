from . import scraper

class TurraScraper(scraper.AlgoliaScraper):
  id = "turra"
  base_url = "https://qzcseio8f2-dsn.algolia.net"
  req_headers = {
    "x-algolia-agent": "Algolia for JavaScript (3.35.1); Browser; Magento2 integration (3.2.0); autocomplete.js 0.38.0",
    "x-algolia-application-id": "QZCSEIO8F2",
    "x-algolia-api-key": "ZmI2NDhlZDY3MDE1NTM4Mzg2MTNmYTZmNmNhZDQ0MzQxOTQxNjQ3YzY3Mjg3NzczNTVlNmIyY2Y2ZGUzYmQzNXRhZ0ZpbHRlcnM9"
  }
  index_name = "live_default_products"
  params = {
    "ruleContexts": '["magento_filters"]',
    "facets": '["categories.level0"]'
  }

  @classmethod
  def algolia_product_object(cls, data):
    return {
      "name": data["name"],
      # turra skus:
      #   1. are random ass numbers with no relation to normal skus
      #   2. arent even in this payload >:(
      "sku": str(data["objectID"]),
      "url": data["url"],
      "price": data["price"]["AUD"]["default"],
      "in_stock": False, # also no instock value that i can grab
    }
