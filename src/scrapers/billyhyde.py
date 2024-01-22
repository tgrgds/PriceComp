from . import scraper

class BillyHydeScraper(scraper.AlgoliaScraper):
  id = "billyhyde"
  base_url = "https://i44xqab9d8-dsn.algolia.net"
  req_headers = {
    "x-algolia-application-id": "I44XQAB9D8",
    "x-algolia-api-key": "NGY4YjA1ZmE4MjdmYmNhYzUzZDBmNTMxM2YxY2ExMDg2YzdlMjkwMmViYjU1OTZkYTJiZDM3YmQ2ZTA3MjUyNnRhZ0ZpbHRlcnM9",
    "content-type": "application/x-www-form-urlencoded",
  }
  index_name = "bhm_default_products"
  params = {
    "ruleContexts":	'["magento_filters"]',
    "facets":	'["price.AUD.default","availability_status","manufacturer"]'
  }

  @classmethod
  def algolia_product_object(cls, data):
    return {
      "name": data["name"],
      "sku": data["sku"],
      "url": data["url"],
      "price": data["price"]["AUD"]["default"],
      "in_stock": data["availability"] == "Yes"
    }
