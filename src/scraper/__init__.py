from src.type import SiteName

from .scrapers import Scraper
from . import better, haworth, mannys, soundseasy, turra, derringers, mooloolaba

SCRAPERS: dict[SiteName, Scraper] = {
  "better": better.BetterScraper,
  "haworth": haworth.HaworthScraper,
  "mannys": mannys.MannysScraper,
  "soundseasy": soundseasy.SoundsEasyScraper,
  "turra": turra.TurraScraper,
  "derringers": derringers.DerringersScraper,
  "mooloolaba": mooloolaba.MooloolabaScraper
}