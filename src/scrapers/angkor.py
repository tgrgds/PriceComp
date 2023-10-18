from math import ceil
import logging

from . import scraper

class AngkorScraper(scraper.Scraper):
  id = "angkor"
  _base_url = "https://api.findify.io/v4/d49855f3-accb-4c6f-b509-91f7de3328c9"

  @classmethod
  def search_query(cls, query: str):
    page = 0

    total_hits = 0

    while True:
      data = {
        "hits": 0,
        "products": []
      }

      params = {
        "user":{
          "uid": "OoYesIpWVtCdVDoa",
          "sid": "EeHr8KKEcLS56DP5",
          "persist": False,
          "exist": True
        },
        "t_client": 1690760668955,
        "limit": 120,
        "offset": 120 * page,
        "q": query
      }

      logging.info(f"Getting page {page}/{ceil(total_hits / 100)}...")

      req = requests.post(
        cls._base_url,
        json=params
      )

      if not req.ok:
        logging.warn(f"Request halted with status {req.status_code}")

      