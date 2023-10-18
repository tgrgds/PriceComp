from . import scraper

class LogansScraper(scraper.AlgoliaScraper):
  id = "logans"
  base_url = "https://2pz2m6w8lw-dsn.algolia.net"
  req_headers = {
    "x-algolia-agent": "Algolia for JavaScript (4.5.1); Browser (lite); instantsearch.js (4.8.3); JS Helper (3.2.2)",
    "x-algolia-api-key": "c8e60316efb533d0d2f2b5150ad0c2a4",
    "x-algolia-application-id": "2PZ2M6W8LW"
  }
  index_name = "shopify_products"
  params = {
    "facets": '["vendor","price","named_tags.lvl0"]'
  }

  @classmethod
  def algolia_product_object(cls, data):
    if not data["sku"]: raise KeyError

    if data["sku"]:
      return {
        "name": data["title"],
        "sku": data["sku"],
        "url": "https://loganspianos.com.au/products/" + data["handle"],
        "price": float(data["price"]),
        "in_stock": data["variants_inventory_count"] > 0
      }
