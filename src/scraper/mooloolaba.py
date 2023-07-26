from . import scrapers

class MooloolabaScraper(scrapers.AlgoliaScraper):
  id = "mooloolaba"
  base_url = "https://ojm1biy2hb-dsn.algolia.net"
  req_headers = {
    "x-algolia-agent": "Algolia for JavaScript (3.35.1); Browser; Magento2 integration (3.2.0); autocomplete.js 0.38.0",
    "x-algolia-application-id": "OJM1BIY2HB",
    "x-algolia-api-key": "50412a3938e9ad6e576c36ccfe4961e3"
  }
  index_name = "pd_products"
  params = {
    "facets": '["brand","price_rounded","categories.lvl0","categories.lvl0"]'
  }

  @classmethod
  def algolia_product_object(cls, data):
    return {
      "name": data["name"],
      "sku": str(data["sku"]),
      "url": "https://www.mooloolabamusic.com.au/" + data["url"],
      "price": float(data["price"]),
      "in_stock": data["in_stock"],
    }
