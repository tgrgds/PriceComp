############
# This takes a list of SKUs via CSV (skus.csv)
# and outputs all known prices from each store
############

import csv, requests
from os import environ

from dotenv import load_dotenv
load_dotenv()

API_URL = environ.get("API_URL")
API_KEY = environ.get("API_KEY")

sites_list = requests.get(f"{API_URL}/api/scraper/list", headers={"Authorization": "Bearer " + API_KEY}).json()
print(sites_list)

with open("skus.csv", "r") as csvfile:
  reader = csv.DictReader(csvfile, ["sku"])

  with open("results.csv", "w") as writefile:
    writer = csv.DictWriter(writefile, fieldnames=["sku"] + [s for s in sites_list])

    writer.writeheader()

    for row in reader:
      results = {}

      stores = requests.get(f"{API_URL}/api/product/search/{row['sku']}?strict=1", headers={"Authorization": "Bearer " + API_KEY})

      if not stores.ok: continue

      stores = stores.json()
      print(stores)

      for store in stores:
        results[store["store_id"]] = store["price"]

      writer.writerow({
        "sku": row["sku"],
        **results
      })