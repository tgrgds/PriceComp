import csv
from json import dump

from src.type import ScraperData

class Scraper:
  @classmethod
  def scrape_all(cls) -> ScraperData:
    raise NotImplementedError

  @classmethod
  def export_all_json(cls, path: str) -> ScraperData:
    data = cls.scrape_all()

    with open(path, "w") as file:
      dump(data, file, indent=2)
      
      file.close()

    return data

  @classmethod
  def export_all_csv(cls, path: str):
    data = cls.scrape_all()

    with open(path, "w", newline="") as csvfile:
      writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
      
      writer.writerow(["sku", "name", "url", "price", "in_stock"])

      for product in data["products"]:
        writer.writerow([
          product["sku"],
          product["name"],
          product["url"],
          product["price"],
          product["in_stock"]
        ])
    
    return data

thing = Scraper()
