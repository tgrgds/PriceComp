from src.type import SiteName

from .scraper import Scraper
from . import (
  better,
  haworth,
  mannys,
  soundseasy,
  turra,
  derringers,
  mooloolaba,
  logans,
  sky,
  djcity,
  mega,
  billyhyde,
)

SCRAPERS: dict[SiteName, Scraper] = {
  "better": better.BetterScraper,
  "haworth": haworth.HaworthScraper,
  "mannys": mannys.MannysScraper,
  "soundseasy": soundseasy.SoundsEasyScraper,
  "turra": turra.TurraScraper,
  "derringers": derringers.DerringersScraper,
  "mooloolaba": mooloolaba.MooloolabaScraper,
  "logans": logans.LogansScraper,
  "sky": sky.SkyScraper,
  "djcity": djcity.DjcityScraper,
  "mega": mega.MegaScraper,
  "billyhyde": billyhyde.BillyHydeScraper,
}
