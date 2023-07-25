from src.type import SiteName

from .scraper import Scraper
from . import better, haworth, mannys, soundseasy, turra

SCRAPERS: dict[SiteName, Scraper] = {
  "better": better.BetterScraper,
  "haworth": haworth.HaworthScraper,
  "mannys": mannys.MannysScraper,
  "soundseasy": soundseasy.SoundsEasyScraper,
  "turra": turra.TurraScraper,
}