from src.type import SiteName

from .scraper import Scraper
from . import better, haworth, mannys

SCRAPERS: dict[SiteName, Scraper] = {
  "better": better.BetterScraper,
  "haworth": haworth.HaworthScraper,
  "mannys": mannys.MannysScraper
}